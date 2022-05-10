import codecs
import math
import os
from itertools import count

import torch

import onmt.translate
from onmt import inputters as inputters
from onmt.utils.misc import tile
from util import debug


def generate_token_mask(atc, node_type_vocab, vocab):
    if atc is None:
        atc = dict()
    token_mask_all = dict()
    allowed_tokens_indices = dict()
    not_allowed_token_indices = dict()
    node_ids = node_type_vocab.stoi.keys()
    for node_id in node_ids:
        if node_id in atc.keys():
            tokens = atc[node_id]
        else:
            tokens = []
        if node_id == '-1':
            tokens = [inputters.EOS_WORD]
        if node_id in ['40', '800', '801', '802']:
            tokens.append(inputters.UNK)
        token_mask = [1. for _ in range(len(vocab))]
        inverse_token_indices = []
        if len(tokens) >= 0:
            token_mask = [1e-20 for _ in range(len(vocab))]
            token_indices = []
            inverse_token_indices = [idx for idx in range(len(vocab))]
            for token in tokens:
                tidx = vocab.stoi[token]
                token_mask[tidx] = 1.0
                token_indices.append(tidx)
                if tidx in inverse_token_indices:
                    inverse_token_indices.remove(tidx)
        allowed_tokens_indices[node_id] = tokens
        token_mask_all[node_id] = torch.FloatTensor(token_mask)
        not_allowed_token_indices[node_id] = inverse_token_indices
    return token_mask_all, allowed_tokens_indices, not_allowed_token_indices
    pass


class TokenTranslator(object):
    """
    Uses a model to translate a batch of sentences.


    Args:
       model (:obj:`onmt.modules.NMTModel`):
          NMT model to use for translation
       fields (dict of Fields): data fields
       beam_size (int): size of beam to use
       n_best (int): number of translations produced
       max_length (int): maximum length output to produce
       global_scores (:obj:`GlobalScorer`):
         object to rescore final translations
       copy_attn (bool): use copy attention during translation
       cuda (bool): use cuda
       beam_trace (bool): trace beam search for debugging
       logger(logging.Logger): logger.
    """

    def __init__(self, model, fields,  beam_size, n_best=1, max_length=100, global_scorer=None, copy_attn=False,
                 logger=None, gpu=False, dump_beam="",  min_length=0, stepwise_penalty=False,
                 block_ngram_repeat=0, ignore_when_blocking=[], sample_rate='16000', window_size=.02,
                 window_stride=.01, window='hamming', use_filter_pred=False, data_type="text",
                 replace_unk=False, report_score=True, report_bleu=False, report_rouge=False,
                 verbose=False, out_file=None, fast=False, option=None):
        self.option = option
        self.logger = logger
        self.gpu = gpu
        self.cuda = gpu > -1

        self.model = model
        self.fields = fields
        self.n_best = n_best
        self.max_length = max_length
        self.global_scorer = global_scorer
        self.copy_attn = copy_attn
        self.beam_size = beam_size
        self.min_length = min_length
        self.stepwise_penalty = stepwise_penalty
        self.dump_beam = dump_beam
        self.block_ngram_repeat = block_ngram_repeat
        self.ignore_when_blocking = set(ignore_when_blocking)
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.window_stride = window_stride
        self.window = window
        self.use_filter_pred = use_filter_pred
        self.replace_unk = replace_unk
        self.data_type = data_type
        self.verbose = verbose
        self.out_file = out_file
        self.report_score = report_score
        self.report_bleu = report_bleu
        self.report_rouge = report_rouge
        self.fast = fast

        # for debugging
        self.beam_trace = self.dump_beam != ""
        self.beam_accum = None
        if self.beam_trace:
            self.beam_accum = {
                "predicted_ids": [],
                "beam_parent_ids": [],
                "scores": [],
                "log_probs": []}

    def translate(self, src_path=None, src_data_iter=None, tgt_path=None, tgt_data_iter=None, src_dir=None,
                  batch_size=None, attn_debug=False, node_type_seq=None, atc=None):
        """
        Translate content of `src_data_iter` (if not None) or `src_path`
        and get gold scores if one of `tgt_data_iter` or `tgt_path` is set.

        Note: batch_size must not be None
        Note: one of ('src_path', 'src_data_iter') must not be None

        Args:
            src_path (str): filepath of source data
            src_data_iter (iterator): an interator generating source data
                e.g. it may be a list or an openned file
            tgt_path (str): filepath of target data
            tgt_data_iter (iterator): an interator generating target data
            src_dir (str): source directory path
                (used for Audio and Image datasets)
            batch_size (int): size of examples per mini-batch
            attn_debug (bool): enables the attention logging

        Returns:
            (`list`, `list`)

            * all_scores is a list of `batch_size` lists of `n_best` scores
            * all_predictions is a list of `batch_size` lists
                of `n_best` predictions
        """
        assert src_data_iter is not None or src_path is not None
        assert node_type_seq is not None, 'Node Types must be provided'
        node_type_scores = node_type_seq[1]
        node_type_seq = node_type_seq[0]
        if batch_size is None:
            raise ValueError("batch_size must be set")
        data = inputters.build_dataset(self.fields,  self.data_type,  src_path=src_path,
                                       src_data_iter=src_data_iter, tgt_path=tgt_path,
                                       tgt_data_iter=tgt_data_iter, src_dir=src_dir,
                                       sample_rate=self.sample_rate, window_size=self.window_size,
                                       window_stride=self.window_stride, window=self.window,
                                       use_filter_pred=self.use_filter_pred)

        if self.cuda:
            cur_device = "cuda"
        else:
            cur_device = "cpu"

        data_iter = inputters.OrderedIterator(
            dataset=data, device=cur_device,
            batch_size=batch_size, train=False, sort=False,
            sort_within_batch=True, shuffle=False)

        builder = onmt.translate.TranslationBuilder(
            data, self.fields,
            self.n_best, self.replace_unk, tgt_path)

        # Statistics
        counter = count(1)
        pred_score_total, pred_words_total = 0, 0
        gold_score_total, gold_words_total = 0, 0

        all_scores = []
        all_predictions = []
        #debug(self.option.tree_count)

        def check_correctness(preds, gold):
            for p in preds:
                if p.strip() == gold.strip():
                    return 1
            return 0

        total_correct = 0

        for bidx, batch in enumerate(data_iter):
            example_idx = batch.indices.item()  # Only 1 item in this batch, guaranteed
            if bidx % 50 == 0:
               debug('Current Example : ', example_idx)
            nt_sequences = node_type_seq[example_idx]
            nt_scores = node_type_scores[example_idx]
            if atc is not None:
                atc_item = atc[example_idx]
            else:
                atc_item = None
            scores = []
            predictions = []
            tree_count = self.option.tree_count
            for type_sequence, type_score in zip(nt_sequences[:tree_count], nt_scores[:tree_count]):
                batch_data = self.translate_batch(batch, data, node_type_str=type_sequence, atc=atc_item)
                translations = builder.from_batch(batch_data)
                already_found = False
                for trans in translations:
                    pred_scores = [score + type_score for score in trans.pred_scores[:self.n_best]]
                    # debug(len(pred_scores))
                    scores += pred_scores
                    pred_score_total += trans.pred_scores[0]
                    pred_words_total += len(trans.pred_sents[0])
                    if tgt_path is not None:
                        gold_score_total += trans.gold_score
                        gold_words_total += len(trans.gold_sent) + 1
                    n_best_preds = [" ".join(pred) for pred in trans.pred_sents[:self.n_best]]
                    gold_sent = ' '.join(trans.gold_sent)
                    correct = check_correctness(n_best_preds, gold_sent)
                    # debug(correct == 1)
                    if not already_found:
                        total_correct += correct
                        already_found = True
                    # debug(len(n_best_preds))
                    predictions += n_best_preds
            all_scores += [scores]
            all_predictions += [predictions]

        if self.dump_beam:
            import json
            json.dump(self.translator.beam_accum,
                      codecs.open(self.dump_beam, 'w', 'utf-8'))
        debug(total_correct)
        return all_scores, all_predictions

    def translate_batch(self, batch, data, node_type_str, atc=None):
        with torch.no_grad():
            return self._fast_translate_batch(batch, data, node_type_str, atc)

    def _fast_translate_batch(self, batch, data, node_type, atc):
        # TODO: faster code path for beam_size == 1.
        # TODO: support these blacklisted features.
        assert data.data_type == 'text'
        assert not self.copy_attn
        assert not self.dump_beam
        assert not self.use_filter_pred
        assert self.block_ngram_repeat == 0
        assert self.global_scorer.beta == 0
        beam_size = self.beam_size
        batch_size = batch.batch_size
        vocab = self.fields["tgt"].vocab
        node_type_vocab = self.fields['tgt_feat_0'].vocab
        start_token = vocab.stoi[inputters.BOS_WORD]
        end_token = vocab.stoi[inputters.EOS_WORD]
        unk_token = vocab.stoi[inputters.UNK]
        _, allowed_tokens, not_allowed_token_indices = generate_token_mask(atc, node_type_vocab, vocab)
        # debug(token_masks.keys())
        assert batch_size == 1, "Only 1 example decoding at a time supported"
        assert (node_type is not None) and isinstance(node_type, str), \
            "Node type string must be provided to translate tokens"

        node_types = [var(node_type_vocab.stoi[n_type.strip()]) for n_type in node_type.split()]
        # node_types.append(var(node_type_vocab.stoi['-1']))
        if self.cuda: node_types = [n_type.cuda() for n_type in node_types]
        # debug(node_types)
        max_length = len(node_types)
        # Encoder forward.
        src = inputters.make_features(batch, 'src', data.data_type)
        _, src_lengths = batch.src
        enc_states, memory_bank = self.model.encoder(src, src_lengths)
        dec_states = self.model.decoder.init_decoder_state(src, memory_bank, enc_states, with_cache=True)
        # Tile states and memory beam_size times.
        dec_states.map_batch_fn(lambda state, dim: tile(state, beam_size, dim=dim))
        memory_bank = tile(memory_bank, beam_size, dim=1)
        memory_lengths = tile(src_lengths, beam_size)
        batch_offset = torch.arange(batch_size, dtype=torch.long, device=memory_bank.device)
        beam_offset = torch.arange(
            0, batch_size * beam_size, step=beam_size, dtype=torch.long, device=memory_bank.device)
        alive_seq = torch.full(
            [batch_size * beam_size, 1], start_token, dtype=torch.long, device=memory_bank.device)
        alive_attn = None
        # Give full probability to the first beam on the first step.
        topk_log_probs = (torch.tensor([0.0] + [float("-inf")] * (beam_size - 1),
                         device=memory_bank.device).repeat(batch_size))
        results = dict()
        results["predictions"] = [[] for _ in range(batch_size)]  # noqa: F812
        results["scores"] = [[] for _ in range(batch_size)]  # noqa: F812
        results["attention"] = [[] for _ in range(batch_size)]  # noqa: F812
        results["gold_score"] = [0] * batch_size
        results["batch"] = batch
        save_attention = [[] for _ in range(batch_size)]
        # max_length += 1
        for step in range(max_length):
            decoder_input = alive_seq[:, -1].view(1, -1, 1)
            curr_node_type = node_types[step]
            node_type_str = str(node_type_vocab.itos[curr_node_type.item()])
            not_allowed_indices = not_allowed_token_indices[node_type_str]
            extra_input = torch.stack([var(2) for _ in range(decoder_input.shape[1])])
            extra_input = extra_input.view(1, -1, 1)
            if self.cuda:
                extra_input = extra_input.cuda()
            final_input = torch.cat((decoder_input, extra_input), dim=-1)
            # Decoder forward.
            dec_out, dec_states, attn = self.model.decoder(
                final_input, memory_bank, dec_states, memory_lengths=memory_lengths,  step=step)
            # Generator forward.
            generator_input = dec_out.squeeze(0)
            # debug(generator_input.shape)
            log_probs = self.model.generator.forward(generator_input)
            vocab_size = log_probs.size(-1)
            # log_probs[:, unk_token] = -1.1e30
            log_probs[:, end_token] = -1.1e10
            log_probs[:, not_allowed_indices] = -1.1e10
            log_probs = torch.log_softmax(log_probs, dim=-1)
            reshaped_topk = topk_log_probs.view(-1).unsqueeze(1)
            # debug(reshaped_topk.shape)
            # debug(topk_log_probs)
            log_probs += reshaped_topk
            attn_probs = attn['std'].squeeze()  # (beam_size, source_length)
            alpha = self.global_scorer.alpha
            length_penalty = ((5.0 + (step + 1)) / 6.0) ** alpha
            # Flatten probs into a list of possibilities.
            curr_scores = log_probs / length_penalty
            curr_scores = curr_scores.reshape(-1, beam_size * vocab_size)
            topk_scores, topk_ids = curr_scores.topk(beam_size, dim=-1)
            # Recover log probs.
            topk_log_probs = topk_scores * length_penalty
            # Resolve beam origin and true word ids.
            topk_beam_index = topk_ids.true_divide(vocab_size)
            topk_ids = topk_ids.fmod(vocab_size)
            # debug(topk_ids)
            beam_indices = topk_beam_index.squeeze().cpu().numpy().tolist()
            if len(attn_probs.shape) == 1:
                attn_to_save = attn_probs[:]
            else:
                attn_to_save = attn_probs[beam_indices , :]
            save_attention[0].append(attn_to_save)
            # Map beam_index to batch_index in the flat representation.
            batch_index = (topk_beam_index + beam_offset[:topk_beam_index.size(0)].unsqueeze(1))
            # Select and reorder alive batches.
            select_indices = batch_index.view(-1).long()

            alive_seq = alive_seq.index_select(0, select_indices)
            memory_bank = memory_bank.index_select(1, select_indices)
            memory_lengths = memory_lengths.index_select(0, select_indices)
            dec_states.map_batch_fn(lambda state, dim: state.index_select(dim, select_indices))
            alive_seq = torch.cat([alive_seq, topk_ids.view(-1, 1)], -1)
        predictions = alive_seq.view(-1, beam_size, alive_seq.size(-1))
        scores = topk_scores.view(-1, beam_size)
        attention = None
        if alive_attn is not None:
            attention = alive_attn.view(alive_attn.size(0), -1, beam_size, alive_attn.size(-1))
        for i in range(len(predictions)):
            b = batch_offset[i]
            for n in range(self.n_best):
                results["predictions"][b].append(predictions[i, n, 1:])
                results["scores"][b].append(scores[i, n])
                if attention is None:
                    results["attention"][b].append([])
                else:
                    results["attention"][b].append(attention[:, i, n, :memory_lengths[i]])
                results["save_attention"] = save_attention
        results["gold_score"] = [0] * batch_size
        if "tgt" in batch.__dict__:
            results["gold_score"] = self._run_target(batch , data)
        return results

    def _from_beam(self, beam):
        ret = {"predictions": [], "scores": [], "attention": []}
        for b in beam:
            n_best = self.n_best
            scores, ks = b.sort_finished(minimum=n_best)
            hyps, attn = [], []
            for i, (times, k) in enumerate(ks[:n_best]):
                hyp, att = b.get_hyp(times, k)
                hyps.append(hyp)
                attn.append(att)
            ret["predictions"].append(hyps)
            ret["scores"].append(scores)
            ret["attention"].append(attn)
        return ret

    def _run_target(self, batch, data):
        data_type = data.data_type
        if data_type == 'text':
            _, src_lengths = batch.src
        else:
            src_lengths = None
        src = inputters.make_features(batch, 'src', data_type)
        tgt_in = inputters.make_features(batch, 'tgt')[:-1]

        #  (1) run the encoder on the src
        enc_states, memory_bank = self.model.encoder(src, src_lengths)
        dec_states = self.model.decoder.init_decoder_state(src, memory_bank, enc_states)
        #  (2) if a target is specified, compute the 'goldScore'
        #  (i.e. log likelihood) of the target under the model
        tt = torch.cuda if self.cuda else torch
        gold_scores = tt.FloatTensor(batch.batch_size).fill_(0)
        dec_out, _, _ = self.model.decoder(tgt_in, memory_bank, dec_states, memory_lengths=src_lengths)

        tgt_pad = self.fields["tgt"].vocab.stoi[inputters.PAD_WORD]
        for dec, tgt in zip(dec_out, batch.tgt[1:].data):
            # Log prob of each word.
            out = self.model.generator.forward(dec)
            tgt = tgt.unsqueeze(1)
            scores = out.data.gather(1, tgt)
            scores.masked_fill_(tgt.eq(tgt_pad), 0)
            gold_scores += scores.view(-1)
        return gold_scores

    def _report_score(self, name, score_total, words_total):
        msg = ("%s AVG SCORE: %.4f, %s PPL: %.4f" % (
            name, score_total / words_total,
            name, math.exp(-score_total / words_total)))
        return msg

    def _report_bleu(self, tgt_path):
        import subprocess
        base_dir = os.path.abspath(__file__ + "/../../..")
        # Rollback pointer to the beginning.
        self.out_file.seek(0)
        print()

        res = subprocess.check_output("perl %s/tools/multi-bleu.perl %s"
                                      % (base_dir, tgt_path),
                                      stdin=self.out_file,
                                      shell=True).decode("utf-8")

        msg = ">> " + res.strip()
        return msg

    def _report_rouge(self, tgt_path):
        import subprocess
        path = os.path.split(os.path.realpath(__file__))[0]
        res = subprocess.check_output(
            "python %s/tools/test_rouge.py -r %s -c STDIN"
            % (path, tgt_path),
            shell=True,
            stdin=self.out_file).decode("utf-8")
        msg = res.strip()
        return msg


# Help functions for working with beams and batches
def var(a):
    if isinstance(a, torch.Tensor):
        return a.clone().detach().requires_grad_(False)
    else:
        return torch.tensor(a, requires_grad=False)

