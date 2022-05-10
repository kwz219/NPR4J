import sys, os
import pickle
import numpy as np

from codit.grammar import JavaGrammar, Rule, ASTNode
from util import debug


def read_all(_file):
    all_ = []
    with open(_file) as f:
        for line in f:
            all_.append(line.split())
    return all_
    pass


if __name__ == '__main__':
    data_path = '/home/saikatc/Research/OpenNMT-py/' \
                   'rule_based_data/raw/all/original_small'
    rule_ppl = 3.5960
    token_ppl = 1.7210

    # data_path = '/home/saikatc/Research/OpenNMT-py/' \
    #             'c_data/raw/all/abstract'
    # rule_ppl = 3.5159
    # token_ppl = 1.7568

    grammar_path = data_path + '/grammar.bin'
    test_dir = data_path + '/test'

    f = open(grammar_path, 'rb')
    grammar = pickle.load(f)
    f.close()
    assert isinstance(grammar, JavaGrammar)
    rules = grammar.rules
    nts = set()
    for rule in rules:
        assert isinstance(rule, Rule)
        nts.add(rule.parent)

    debug(len(nts))
    num_rules = []
    child_length_all = []
    for nt in nts:
        nt_rules = grammar[nt]
        childs_lengths = []
        for rule in nt_rules:
            len_childs = len(rule.children)
            childs_lengths.append(len_childs)
            child_length_all.append(len_childs)
        avg_child = np.mean(childs_lengths)
        # debug(avg_child)
        # child_length_all.append(avg_child)
        # debug(nt, '->',  len(nt_rules))
        num_rules.append(len(nt_rules))

    # debug(np.mean(child_length_all))
    # debug(num_rules)
    mean = np.mean(num_rules)
    median = np.median(num_rules)
    # debug(mean, median)

    frontier_file = test_dir + '/next.frontier'
    frontiers = read_all(frontier_file)
    all_example_options = []
    total_ways_f = []
    all_frontier_lengths = []

    for ex_idx, example_frontier in enumerate(frontiers):
        example_cands_number = 1
        total_rule_ways = 1
        # total_ways_f.append(np.power(rule_ppl, len(example_frontier)))
        for fid, frontier in enumerate(example_frontier):
            rule_head = ASTNode(frontier)
            candidate_options = grammar[rule_head]
            total_rule_ways *= min(rule_ppl, len(candidate_options))
            example_cands_number *= (len(candidate_options))
            # if fid == 0:
            #     debug(rule_head, len(candidate_options))
        total_ways_f.append(total_rule_ways)
        all_example_options.append(example_cands_number)

    print('All_Tree ', np.mean(all_example_options), float(np.max(all_example_options)),
          float(np.min(all_example_options)), sep='\t')

    next_token_file = test_dir + '/next.token'
    all_tokens = read_all(next_token_file)
    all_token_lengths = []
    total_ways = []
    for tokens in all_tokens:
        all_token_lengths.append(len(tokens))
        total_ways.append(np.power(token_ppl, len(tokens)))
    # debug(np.mean(all_token_lengths), '\t', float(np.max(all_token_lengths)), '\t', float(np.min(all_token_lengths)))
    print('Prob_Token', np.mean(total_ways),  float(np.max(total_ways)),  float(np.min(total_ways)), sep='\t')
    print('Prob_Tree', np.mean(total_ways_f), float(np.max(total_ways_f)), float(np.min(total_ways_f)), sep='\t')


