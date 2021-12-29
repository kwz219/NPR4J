# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This CoCoNut code is licensed under the license found in the LICENSE file in
# the root directory of this CoCoNut tree. An additional grant of patent rights
# can be found in the PATENTS file in the same directory.

import numpy as np
import torch

from fairseq import utils


from transformers import GPT2Tokenizer

from fairseq.data import data_utils, LanguagePairDataset


def collate(
    samples, pad_idx, eos_idx, left_pad_source=True, left_pad_target=False,
    input_feeding=True,
):
    if len(samples) == 0:
        return {}

    def merge(key, left_pad, move_eos_to_beginning=False):
        return data_utils.collate_tokens(
            [s[key] for s in samples],
            pad_idx, eos_idx, left_pad, move_eos_to_beginning,
        )

    id = torch.LongTensor([s['id'] for s in samples])

    ctx_tokens = merge('context', left_pad=left_pad_source)
    ctx_types = merge('ctx_types', left_pad=left_pad_source)

    assert len(ctx_types)==len(ctx_types)

    ctx_lengths = torch.LongTensor([s['context'].numel() for s in samples])
    ctx_lengths, sort_order = ctx_lengths.sort(descending=True)
    id = id.index_select(0, sort_order)

    ctx_tokens = ctx_tokens.index_select(0, sort_order)
    ctx_types = ctx_types.index_select(0, sort_order)

    prev_output_tokens = None
    target = None
    if samples[0].get('target', None) is not None:
        target = merge('target', left_pad=left_pad_target)
        target = target.index_select(0, sort_order)
        ntokens = sum(len(s['target']) for s in samples)

        if input_feeding:
            # we create a shifted version of targets for feeding the
            # previous output token(s) into the next decoder step
            prev_output_tokens = merge(
                'target',
                left_pad=left_pad_target,
                move_eos_to_beginning=True,
            )
            prev_output_tokens = prev_output_tokens.index_select(0, sort_order)
    else:
        ntokens = sum(len(s['context']) for s in samples)

    batch = {
        'id': id,
        'ntokens': ntokens,
        'net_input': {
            'ctx_tokens': ctx_tokens,
            'ctx_lengths': ctx_lengths,
            'ctx_types': ctx_types,
        },
        'target': target,
        'nsentences': samples[0]['context'].size(0),
    }
    if prev_output_tokens is not None:
        batch['net_input']['prev_output_tokens'] = prev_output_tokens
    return batch


class GPT2LanguagePairWithContextDataset(LanguagePairDataset):
    """
    A pair of torch.utils.data.Datasets.

    Args:
        src (torch.utils.data.Dataset): CoCoNut dataset to wrap
        src_sizes (List[int]): CoCoNut sentence lengths
        src_dict (~fairseq.data.Dictionary): CoCoNut vocabulary
        tgt (torch.utils.data.Dataset, optional): target dataset to wrap
        tgt_sizes (List[int], optional): target sentence lengths
        tgt_dict (~fairseq.data.Dictionary, optional): target vocabulary
        left_pad_source (bool, optional): pad CoCoNut tensors on the left side.
            Default: ``True``
        left_pad_target (bool, optional): pad target tensors on the left side.
            Default: ``False``
        max_source_positions (int, optional): max number of tokens in the CoCoNut
            sentence. Default: ``1024``
        max_target_positions (int, optional): max number of tokens in the target
            sentence. Default: ``1024``
        shuffle (bool, optional): shuffle dataset elements before batching.
            Default: ``True``
        input_feeding (bool, optional): create a shifted version of the targets
            to be passed into the model for input feeding/teacher forcing.
            Default: ``True``
        remove_eos_from_source (bool, optional): if set, removes eos from end of
            CoCoNut if it's present. Default: ``False``
        append_eos_to_target (bool, optional): if set, appends eos to end of
            target if it's absent. Default: ``False``
    """

    def __init__(self, *args, **kwargs):
        super(GPT2LanguagePairWithContextDataset,self).__init__(*args, **kwargs)
        additional_tokens=['CaMeL','$NUMBER$','$STRING$']
        self.tokenizer=GPT2Tokenizer.from_pretrained("microsoft/CodeGPT-small-java")
        self.tokenizer.add_tokens(additional_tokens)
        self.sep_index=100000


    def getsubindex(self,list, sublist):
        listr = ' '.join([str(i) for i in list])
        sublistr = ' '.join([str(i) for i in sublist])
        start_idx=listr.index(sublistr) // 2
        end_idx=start_idx+len(sublist)
        return start_idx,end_idx
    def __getitem__(self, index):
        tgt_item = self.tgt[index] if self.tgt is not None else None
        src_item = self.src[index]
        ctx_item = src_item
        ctx_types = torch.zeros(ctx_item.size())
        for i,token in enumerate(src_item):
          #这里分开了
          if token == self.sep_index:
            ctx_types = src_item[(i+1):]
            ctx_item = src_item[:i]

            break

        # Append EOS to end of tgt sentence if it does not have an EOS and remove
        # EOS from end of src sentence if it exists. This is useful when we use
        # use existing datasets for opposite directions i.e., when we want to
        # use tgt_dataset as src_dataset and vice versa
        if self.append_eos_to_target:
            eos = self.tokenizer.eos_token_id
            if self.tgt and self.tgt[index][-1] != eos:
                tgt_item = torch.cat([self.tgt[index], torch.LongTensor([eos])])

        if self.remove_eos_from_source:
            eos = self.tokenizer.eos_token_id
            if self.src[index][-1] == eos:
                src_item = self.src[index][:-1]

        return {
            'id': index,
            'context': ctx_item,
            'target': tgt_item,
            'ctx_types': ctx_types
        }

    def __len__(self):
        return len(self.src)

    def collater(self, samples):
        """Merge a list of samples to form a mini-batch.

        Args:
            samples (List[dict]): samples to collate

        Returns:
            dict: a mini-batch with the following keys:

                - `id` (LongTensor): example IDs in the original input order
                - `ntokens` (int): total number of tokens in the batch
                - `net_input` (dict): the input to the Model, containing keys:

                  - `src_tokens` (LongTensor): a padded 2D Tensor of tokens in
                    the CoCoNut sentence of shape `(bsz, src_len)`. Padding will
                    appear on the left if *left_pad_source* is ``True``.
                  - `src_lengths` (LongTensor): 1D Tensor of the unpadded
                    lengths of each CoCoNut sentence of shape `(bsz)`
                  - `ctx_tokens` (LongTensor)
                  - `ctx_lengths` (LongTensor)
                  - `prev_output_tokens` (LongTensor): a padded 2D Tensor of
                    tokens in the target sentence, shifted right by one position
                    for input feeding/teacher forcing, of shape `(bsz,
                    tgt_len)`. This key will not be present if *input_feeding*
                    is ``False``. Padding will appear on the left if
                    *left_pad_target* is ``True``.

                - `target` (LongTensor): a padded 2D Tensor of tokens in the
                  target sentence of shape `(bsz, tgt_len)`. Padding will appear
                  on the left if *left_pad_target* is ``True``.
        """
        return collate(
            samples, pad_idx=self.tokenizer.pad_token_id, eos_idx=self.tokenizer.eos_token_id,
            left_pad_source=self.left_pad_source, left_pad_target=self.left_pad_target,
            input_feeding=self.input_feeding,
        )
    def dummy_sentence(self, length):
        t = torch.Tensor(length).uniform_(1, self.tokenizer.vocab_size).long()
        t[-1] = self.tokenizer.eos_token_id
        return t
    def get_dummy_batch(self, num_tokens, max_positions, src_len=128, tgt_len=128):
        """Return a dummy batch with a given number of tokens."""
        src_len, tgt_len = utils.resolve_max_positions(
            (src_len, tgt_len),
            max_positions,
            (self.max_source_positions, self.max_target_positions),
        )

        bsz = max(num_tokens // max(src_len, tgt_len), 1)
        return self.collater([
            {
                'id': i,
                'target': self.dummy_sentence(tgt_len) ,
                'context': self.dummy_sentence(src_len),
                'ctx_types': self.dummy_sentence(src_len),
            }
            for i in range(bsz)
        ])

    def prefetch(self, indices):
        self.src.prefetch(indices)
        self.tgt.prefetch(indices)

    @property
    def supports_prefetch(self):
        return (
            hasattr(self.src, 'supports_prefetch')
            and self.src.supports_prefetch
            and hasattr(self.tgt, 'supports_prefetch')
            and self.tgt.supports_prefetch
        )
