#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import argparse

import numpy as np
from nltk.translate import bleu_score

import CODIT.onmt.opts
from CODIT.codit.grammar import JavaGrammar
from CODIT.codit.hypothesis import Hypothesis
from CODIT.onmt.translate.translator import build_translator
from CODIT.onmt.utils.logging import init_logger


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

        blue = bleu_score.sentence_bleu([ref], hyp,
                                        smoothing_function=bleu_score.SmoothingFunction().method3)
        blue_scores.append(blue)
    return blue_scores


def print_bleu_res_to_file(b_file, bls):
    if isinstance(bls, np.ndarray):
        r = bls.shape[0]
        for i in range(r):
            min_ed = min(bls[i][1:])
            s = str(i) + ',' + ','.join([str(x) for x in bls[i]]) + ',' + str(min_ed)

            b_file.write(s + '\n')
        # first_cand_bleus = [x[0] if len(x) > 0 else 0.0 for x in bls ]
        # avg_cand_bleus = [np.mean(x) if len(x) > 0 else 0.0 for x in bls]
        # cand_max_bleus = [np.max(x) if len(x) > 0 else 0.0 for x in bls]
        # print np.mean(first_cand_bleus), np.mean(avg_cand_bleus), np.mean(cand_max_bleus)
        # return np.mean(first_cand_bleus), np.mean(avg_cand_bleus), np.mean(cand_max_bleus)
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


java_keywords = ["abstract", "continue", "for", "new", "switch", "assert", "default", "goto", "package", "synchronized",
                 "boolean", "do", "if", "private", "this", "break", "double", "implements", "protected", "throw",
                 "byte", "else", "import", "public", "throws", "case", "enum", "instanceof", "return", "transient",
                 "catch", "extends", "int", "short", "try", "char", "final", "interface", "static", "void", "class",
                 "finally", "long", "strictfp", "volatile", "const", "float", "native", "super", "while"]
java_keywords.extend([t for t in '~`!@#$%^&*()-+={[}]|\\:;\"\'<,>.?'])
for c1 in '~`!@#$%^&*()-+={[}]|\\:;\"\'<,>.?':
    for c2 in '~`!@#$%^&*()-+={[}]|\\:;\"\'<,>.?':
        java_keywords.extend(c1 + c2)
import re
identifier = re.compile('[A-Za-z_]+[A-Za-z0-9]*(\\.[A-Za-z_]+[A-Za-z0-9]*)*')


def is_there_new_token_in_tgt(src, tgt):
    src = src.strip()
    tgt = tgt.strip()
    s_parts = src.split()
    s_parts = [s.strip() for s in s_parts]
    t_parts = set(tgt.split())
    for tt in t_parts:
        tt = tt.strip()
        if tt in s_parts or tt in java_keywords:
            continue
        elif re.match(identifier, tt):
            return True
    return False
    pass


def main(opt):
    translator = build_translator(opt, report_score=True)
    all_scores, all_cands = translator.translate(src_path=opt.src,
                                                 tgt_path=opt.tgt,
                                                 src_dir=opt.src_dir,
                                                 batch_size=opt.batch_size,
                                                 attn_debug=opt.attn_debug)
    beam_size = actual_n_best  # len(all_scores[0])
    exp_name = opt.name
    all_sources = []
    all_targets = []
    tgt_file = open(opt.tgt)
    src_file = open(opt.src)
    for a, b in zip(src_file, tgt_file):
        all_sources.append(a.strip())
        all_targets.append(b.strip())
    tgt_file.close()
    src_file.close()
    correct = 0
    no_change = 0
    decode_res_file = open('full_report/details/' + exp_name + '_' + str(beam_size) + '_s2s.txt', 'w')
    bleu_file = open('full_report/bleu_scores/' + exp_name + '_' + str(beam_size) + '_s2s.csv', 'w')
    correct_id_file = open('full_report/correct_ids/' + exp_name + '_' + str(beam_size) + 's2s.txt', 'w')

    all_bleus = []
    total_example = 0
    new_token_added_total_count = 0
    new_token_added_of_correct_examples = 0
    for idx, (src, tgt, cands) in enumerate(zip(all_sources, all_targets, all_cands)):
        total_example += 1
        decode_res_file.write(str(idx) + '\n')
        decode_res_file.write(src + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        decode_res_file.write(tgt + '\n')
        n_token_added = is_there_new_token_in_tgt(src, tgt)
        if n_token_added:
            new_token_added_total_count += 1
        if src == tgt:
            no_change += 1
        decode_res_file.write('=====================================================================================\n')
        decode_res_file.write('Canditdate Size : ' + str(len(cands)) + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        bleus = []
        found = False
        bleus.append(get_edit_dist(src, tgt))
        for cand in cands:
            ed = get_edit_dist(tgt, cand)
            if ed == 0:
                found = True
            bleus.append(ed)
            decode_res_file.write(cand + '\n')
            decode_res_file.write(str(ed) + '\n')
        if found:
            if n_token_added:
                new_token_added_of_correct_examples += 1
            correct += 1
            correct_id_file.write(str(idx) + '\n')
        all_bleus.append(bleus)
        decode_res_file.write(str(found) + '\n\n')

    all_bleus = np.asarray(all_bleus)
    print_bleu_res_to_file(bleu_file, all_bleus)
    decode_res_file.close()
    bleu_file.close()
    correct_id_file.close()
    print({
        'Correct': correct,
	'fully-concretizable': total_examples - new_token_added_of_correct_examples
        'Total': total_example
    })


if __name__ == "__main__":
    import warnings

    warnings.filterwarnings('ignore')
    parser = argparse.ArgumentParser(
        description='translate_token.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    onmt.opts.add_md_help_argument(parser)
    onmt.opts.translate_opts(parser)
    parser.add_argument('--name', help='Name of the Experiment', required=True)

    opt = parser.parse_args()
    actual_n_best = opt.n_best
    logger = init_logger(opt.log_file)
    # print(create_tree_from_candidates(['2018 688 1624 1913 1606 469'], grammar))
    main(opt)
