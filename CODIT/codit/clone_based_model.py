import pickle
import sys, os
import numpy as np
from util import read_file, generate_tree_from_rule_str, generate_terminal_node_sequence, get_tree_edit_distance, debug


def get_k_most_similar_train_example(test_tree, train_src_tree, k):
    if test_tree is None:
        indices = np.random.randint(low=0, high=len(train_src_tree)-1, size=(k))
        return indices
    dists = []
    for tr_idx, train_tree in enumerate(train_src_tree):
        if tr_idx % 1000 == 0:
            debug(tr_idx)
        if train_tree is not None:
            dist = get_tree_edit_distance(test_tree, train_tree)
        else:
            dist = 99999
        dists.append(dist)
    indices = np.argsort(dists)[:k]
    return indices
    pass


def clone_based_structural_transformation(train_rule_src, train_rule_tgt,
                                          src_struct, k=100, grammar_file=None, file=None):
    assert grammar_file is not None, 'Grammar must be provided'
    f = open(grammar_file, 'rb')
    grammar = pickle.load(f)
    f.close()
    if file is None:
        outp = sys.stdout
    else:
        outp = open(file, 'w')

    test_examples = read_file(src_struct)
    train_src_examples = read_file(train_rule_src)
    train_tgt_examples = read_file(train_rule_tgt)
    test_trees = [generate_tree_from_rule_str(rule_str, grammar) for rule_str in test_examples]
    train_src_trees = [generate_tree_from_rule_str(rule_str, grammar) for rule_str in train_src_examples]
    train_tgt_node_seqs = [generate_terminal_node_sequence(rule_str, grammar) for rule_str in train_tgt_examples]

    for tidx, example in enumerate(test_trees):
        debug(tidx)
        train_indices = get_k_most_similar_train_example(example, train_src_trees, k)
        debug(train_indices)
        node_sequences = []
        for index in train_indices:
            if train_tgt_node_seqs[index] is not None:
                node_sequences.append(' '.join(train_tgt_node_seqs[index]))
        if len(node_sequences) == 0:
            node_sequences.append(' '.join(example.get_leaf_typ_sequence()))
        wstr = '\t'.join(node_sequences)
        outp.write(wstr + '\n')
        outp.flush()
    if file:
        outp.close()
    pass
