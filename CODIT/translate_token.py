#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import argparse
import copy
import pickle
import sys

import numpy as np
from nltk.translate import bleu_score

import onmt.opts
from CODIT.codit.grammar import JavaGrammar
from onmt.translate.translator import build_translator
from onmt.utils.logging import init_logger
from CODIT.translate_structure import get_edit_dist
from CODIT.util import write_dummy_generated_node_types, debug


def get_bleu_score(original_codes, generated_top_result):
    blue_scores = []
    for reference, hypothesis in zip(original_codes, generated_top_result):
        ref = []
        for x in reference.split(' '):
            if x.strip() != '':
                ref.append(x.strip())
        hyp = []
        for x in hypothesis.split(' '):
            if x.strip() != '':
                hyp.append(x.strip())
        blue = bleu_score.sentence_bleu([ref], hyp, smoothing_function=bleu_score.SmoothingFunction().method3)
        blue_scores.append(blue)
    return blue_scores


def print_bleu_res_to_file(b_file, bls):
    if isinstance(bls, np.ndarray):
        r = bls.shape[0]
        for i in range(r):
            s = str(i) + ','
            s += ','.join([str(x) for x in bls[i]])
            s += ',' + str(np.min(bls[i][1:]))
            b_file.write(s + '\n')
        first_cand_bleus = [x[0] if len(x) > 0 else 0.0 for x in bls]
        avg_cand_bleus = [np.mean(x) if len(x) > 0 else 0.0 for x in bls]
        cand_max_bleus = [np.max(x) if len(x) > 0 else 0.0 for x in bls]
        return np.mean(first_cand_bleus), np.mean(avg_cand_bleus), np.mean(cand_max_bleus)
    pass


def get_all_node_type_str(file_path):
    node_types, all_scores = [], []
    with open(file_path) as inp:
        for line in inp:
            line = line.strip()
            parts = line.split('\t')
            node_sequences = []
            scores = []
            for part in parts:
                score_parts = part.split('/')
                node_sequences.append(score_parts[0])
                if len(score_parts) > 1:
                    scores.append(float(score_parts[1]))
                else:
                    scores.append(1.0)
            node_types.append(node_sequences)
            all_scores.append(scores)
        inp.close()
        return node_types, all_scores
    pass


def process_source(src_str):
    src_str = src_str.strip()
    words = src_str.split()
    src_modified = [word.split(u"|")[0] for word in words]
    return ' '.join(src_modified)
    pass


def re_organize_candidates(cands, scores, src, n_best):
    all_scores = []
    for cand, score in zip(cands, scores):
        all_scores.append(score.cpu())
    sorted_indices = np.argsort(all_scores)
    reformatted = []
    taken_cands = set()
    for i in sorted_indices:
        if str(cands[sorted_indices[i]]) not in taken_cands:
            reformatted.append(cands[sorted_indices[i]])
            taken_cands.add(str(cands[sorted_indices[i]]))
    return reformatted[:n_best]
    pass


def extract_atc_from_grammar(grammar_file):
    f = open(grammar_file, 'rb')
    grammar = pickle.load(f)
    f.close()
    assert isinstance(grammar, JavaGrammar)
    value_node_rules = grammar.value_node_rules
    return value_node_rules
    pass


def refine_atc(all_atcs, atc_file):
    f = open(atc_file, 'rb')
    code_atcs = pickle.load(f)
    f.close()
    new_atcs = []
    for i in range(len(all_atcs)):
        atc = copy.copy(all_atcs[i])
        atc['40'] = [token for token in code_atcs[i]['40']]
        atc['800'] = [token for token in code_atcs[i]['800']]
        atc['801'] = [token for token in code_atcs[i]['801']]
        atc['802'] = [token for token in code_atcs[i]['802']]
        new_atcs.append(atc)
    return new_atcs
    pass


def main(opt):
    grammar_atc = extract_atc_from_grammar(opt.grammar)
    all_node_type_seq_str, node_seq_scores = get_all_node_type_str(opt.tmp_file)
    total_number_of_test_examples = len(all_node_type_seq_str)
    all_atcs = [grammar_atc for _ in range(total_number_of_test_examples)]
    if opt.atc is not None:
        all_atcs = refine_atc(all_atcs, opt.atc)
    translator = build_translator(opt, report_score=True, multi_feature_translator=True)
    all_scores, all_cands = translator.translate(
        src_path=opt.src, tgt_path=opt.tgt, src_dir=opt.src_dir, batch_size=opt.batch_size, attn_debug=opt.attn_debug,
        node_type_seq=[all_node_type_seq_str, node_seq_scores], atc=all_atcs)
    beam_size = len(all_scores[0])
    exp_name = opt.name
    all_sources, all_targets = [], []
    tgt_file = open(opt.tgt)
    src_file = open(opt.src)
    for a, b in zip(src_file, tgt_file):
        all_sources.append(process_source(a.strip()))
        all_targets.append(process_source(b.strip()))
    tgt_file.close()
    src_file.close()
    correct, no_change = 0, 0
    decode_res_file = open('full_report/details/' + exp_name + '_' + str(beam_size) + '_codit_result.txt', 'w')
    all_eds = []
    total_example = 0
    correct_ids_file = open('full_report/correct_ids/' + exp_name + '_' + str(beam_size) + '_codit_result.txt', 'w')
    for idx, (src, tgt, cands, scores) in enumerate(zip(all_sources, all_targets, all_cands, all_scores)):
        total_example += 1
        decode_res_file.write(str(idx) + '\n')
        decode_res_file.write(src + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        decode_res_file.write(tgt + '\n')
        if src == tgt:
            no_change += 1
        eds = []
        o_ed = get_edit_dist(src, tgt)
        eds.append(o_ed)
        decode_res_file.write('=====================================================================================\n')
        decode_res_file.write('Canditdate Size : ' + str(len(cands)) + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')

        found = False
        cands_reformatted = re_organize_candidates(cands, scores, src, opt.n_best)
        for cand in cands_reformatted:
            ed = get_edit_dist(tgt, cand)
            if cand == tgt:
                found = True
            eds.append(ed)
            decode_res_file.write(cand + '\n')
            decode_res_file.write(str(ed) + '\n')
        if found:
            correct += 1
            correct_ids_file.write(str(idx) + '\n')
        all_eds.append(eds)
        decode_res_file.write(str(found) + '\n\n')
        decode_res_file.flush()
        if idx % 100 == 0:
            debug("Processed %d examples so far, found %d correct!" % (idx, correct))

    ed_file = open('full_report/edit_distances/' + exp_name +
                   '-' + str(correct) + '-' + str(opt.tree_count) + '-' +
                   '-' + str(opt.n_best) + 'eds.csv', 'w')
    all_eds = np.asarray(all_eds)
    print_bleu_res_to_file(ed_file, all_eds)
    decode_res_file.close()
    ed_file.close()
    correct_ids_file.close()
    print(correct, total_example)


if __name__ == "__main__":
    data = 'code_change_data'
    bs = 10
    parser = argparse.ArgumentParser(
        description='translate_token.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    onmt.opts.add_md_help_argument(parser)
    onmt.opts.translate_opts(parser)
    # data = '10-20'
    parser.add_argument('--name', help='Name of the Experiment', default=data + '/golden_types')
    parser.add_argument('--tmp_file', default='data/raw/' + data + '/test/next.token.id')
    parser.add_argument('--grammar', default='data/raw/' + data + '/grammar.bin')
    parser.add_argument('--atc', default='data/raw/' + data + '/test/atc_scope.bin')
    parser.add_argument('--tree_count', type=int, default=1)
    opt = parser.parse_args()
    opt.batch_size = 1
    opt.model = '/home/saikatc/Research/Codit/models/' + data + '/augmented.token-best-acc.pt'
    opt.src = '/home/saikatc/Research/Codit/data/raw/' + data + '/test/prev.augmented.token'
    opt.tgt = '/home/saikatc/Research/Codit/data/raw/' + data + '/test/next.augmented.token'
    opt.gpu = 0
    opt.beam_size = bs
    opt.n_best = bs
    logger = init_logger(opt.log_file)
    main(opt)
