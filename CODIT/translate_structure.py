#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals
import argparse
import pickle

import numpy as np
import torch
from nltk.translate import bleu_score

from CODIT.codit.grammar import JavaGrammar
from onmt.utils.logging import init_logger
from onmt.translate.translator import build_translator

import onmt.opts
from CODIT.util import debug
from CODIT.codit.hypothesis import Hypothesis


def get_edit_dist(org_code, cand_code):
    org_parts = [part.strip() for part in org_code.split()]
    cand_parts = [part.strip() for part in cand_code.split()]

    def levenshteinDistance(s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    return levenshteinDistance(org_parts, cand_parts)
    pass


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

        blue = bleu_score.sentence_bleu([ref], hyp ,
                                        smoothing_function=bleu_score.SmoothingFunction().method3)
        blue_scores.append(blue)
    return blue_scores


def print_bleu_res_to_file(b_file, bls):
    if isinstance(bls, np.ndarray):
        r = bls.shape[0]
        for i in range(r):
            s = ','.join([str(x) for x in bls[i]])
            b_file.write(s + '\n')
        #first_cand_bleus = [x[0] if len(x) > 0 else 0.0 for x in bls ]
        #avg_cand_bleus = [np.mean(x) if len(x) > 0 else 0.0 for x in bls]
        #cand_max_bleus = [np.max(x) if len(x) > 0 else 0.0 for x in bls]
        #print np.mean(first_cand_bleus), np.mean(avg_cand_bleus), np.mean(cand_max_bleus)
        #return np.mean(first_cand_bleus), np.mean(avg_cand_bleus), np.mean(cand_max_bleus)
    pass


def create_tree_from_candidates(cands, grammar):
    assert isinstance(grammar, JavaGrammar)
    trees = []
    for rule_id_str in cands:
        try:
            rules = [int(rule) for rule in rule_id_str.split()]
            hyp = Hypothesis(grammar)
            for rule_id in rules:
                c_rule = grammar.id_to_rule[rule_id]
                hyp.apply_rule(c_rule)
            terminal_seq = hyp.get_terminal_sequence()
            trees.append(terminal_seq)
        except:
            trees.append(None)
    return trees
    pass


def generate_all_tree_candidates(all_cands, all_scores, grammar, actual_n_best, src_file):
    debug(actual_n_best)
    all_filtered_trees = []
    all_filtered_cands = []
    all_filtered_scores = []
    inp = open(src_file)
    for i, (cands, scores, line) in enumerate(zip(all_cands, all_scores, inp)):
        line = line.strip()
        filtered_trees, filtered_cands, filtered_scores = [], [], []
        trees = create_tree_from_candidates(cands, grammar)
        actual_src_tree = create_tree_from_candidates([line], grammar)[0]
        filtered_cands.append(line)
        if actual_src_tree is None:
            debug('Original Tree Cannot be generated from this source', line)
        filtered_trees.append(actual_src_tree)
        filtered_scores.append(-1e20)
        for tree, cand, score in zip(trees, cands, scores):
            if tree is not None:
                filtered_cands.append(cand)
                filtered_trees.append(tree)
                if isinstance(score, torch.Tensor):
                    filtered_scores.append(float(score.item()))
                else:
                    filtered_scores.append(score)
        if len(filtered_scores) < 2:
            debug('No Tree generated from example ', i)
        else:
            filtered_scores[0] = filtered_scores[1]
        all_filtered_cands.append(filtered_cands[:actual_n_best])
        all_filtered_trees.append(filtered_trees[:actual_n_best])
        all_filtered_scores.append(filtered_scores[:actual_n_best])
    inp.close()
    return all_filtered_cands, all_filtered_trees, all_filtered_scores
    pass


def translate_all(opt, grammar, actual_n_best):
    translator = build_translator(opt, report_score=True)
    all_scores, all_cands = translator.translate(
        src_path=opt.src, tgt_path=opt.tgt, src_dir=opt.src_dir, batch_size=opt.batch_size, attn_debug=opt.attn_debug)
    all_cands, all_trees, all_scores = generate_all_tree_candidates(
        all_cands, all_scores, grammar, actual_n_best, opt.src)
    return all_scores, all_cands, all_trees


def main(opt, grammar, actual_n_best):
    all_scores, all_cands, all_tree_cands = translate_all(opt, grammar, actual_n_best)
    beam_size = actual_n_best
    exp_name = opt.name
    all_sources, all_targets = [], []
    tgt_file = open(opt.tgt)
    src_file = open(opt.src)
    for a, b in zip(src_file, tgt_file):
        all_sources.append(a.strip())
        all_targets.append(b.strip())
    tgt_file.close()
    src_file.close()
    correct, no_change = 0, 0
    decode_res_file = open('full_report/details/' + exp_name + '_' + str(beam_size) + '.txt', 'w')
    bleu_file = open('full_report/bleu_scores/' + exp_name + '_'+ str(beam_size) + '.csv', 'w')
    correct_id_file = open('full_report/correct_ids/' + exp_name + '_' + str(beam_size) + '.txt', 'w')
    all_bleus = []
    total_example = 0
    for idx, (src, tgt, cands, trees) in enumerate(zip(all_sources, all_targets, all_cands, all_tree_cands)):
        total_example += 1
        decode_res_file.write(str(idx) + '\n')
        decode_res_file.write(src + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        decode_res_file.write(tgt + '\n')
        if src == tgt:
            no_change += 1
        decode_res_file.write('=====================================================================================\n')
        decode_res_file.write('Canditdate Size : ' + str(len(cands)) + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        bleus = []
        found = False
        debug(len(cands), len(trees))
        for cand, tree in zip(cands, trees):
            ed = get_edit_dist(tgt, cand)
            if cand == tgt:
                found = True
            bleus.append(ed)
            decode_res_file.write(cand + '\n')
            decode_res_file.write(' '.join([str(x) for x in tree]) + '\n')
            decode_res_file.write(str(ed) + '\n')
        if found:
            correct += 1
            correct_id_file.write(str(idx) + '\n')
        all_bleus.append(bleus)
        decode_res_file.write(str(found) + '\n\n')

    all_bleus = np.asarray(all_bleus)
    print_bleu_res_to_file(bleu_file, all_bleus)
    decode_res_file.close()
    bleu_file.close()
    correct_id_file.close()
    print(correct, no_change, total_example)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='translate_token.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    onmt.opts.add_md_help_argument(parser)
    onmt.opts.translate_opts(parser)
    parser.add_argument('--name', help='Name of the Experiment', required=True)
    parser.add_argument('--grammar', help='Path of the grammar file', required=True)

    opt = parser.parse_args()
    opt.beam_size *= 2
    actual_n_best = opt.n_best
    opt.n_best = opt.beam_size
    logger = init_logger(opt.log_file)
    f = open(opt.grammar, 'rb')
    debug('Loading the Grammar')
    grammar = pickle.load(f)
    debug('Grammar Loaded From : %s' % opt.grammar)
    assert isinstance(grammar, JavaGrammar)
    # print(create_tree_from_candidates(['2018 688 1624 1913 1606 469'], grammar))
    main(opt, grammar, actual_n_best)
