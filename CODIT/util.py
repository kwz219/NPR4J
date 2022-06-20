import inspect
import os
from datetime import datetime
from sys import stderr

from apted import APTED, Config
from CODIT.codit.hypothesis import Hypothesis
import numpy as np


def debug(*msg):
    time = datetime.now()
    timestr = str(time.strftime('%X'))
    import inspect
    file_path = inspect.stack()[1][1]
    line_num = inspect.stack()[1][2]
    file_name = file_path
    if os.getcwd() in file_path:
        file_name = file_path[len(os.getcwd())+1:]
    stack = str(file_name) + '#' + str(line_num) + ' [' + timestr + ']'
    print(stack, end=' ', file=stderr)
    res = '\t'
    for ms in msg:
        res += (str(ms) + ' ')
    print(res, file=stderr)


def sample_roulette_wheel(prob_dist):
    cum_dist = np.cumsum(prob_dist)
    random = np.random.uniform(0, 1)
    sz = len(cum_dist)
    for i in range(sz):
        if cum_dist[i] >= random:
            return i


def write_dummy_generated_node_types(input_file, output_file):
    with open(input_file) as inp:
        with open(output_file, 'w') as out:
            for line in inp:
                line = line.strip()
                words = line.split()
                seq_str = []
                for word in words:
                    parts = word.split(u"|")
                    seq_str.append(parts[1])
                wstr = ' '.join(seq_str)
                out.write(wstr + '\n')
            out.close()
            inp.close()
    pass


def read_file(file_path):
    with open(file_path) as fp:
        lines = [line.strip() for line in fp]
        fp.close()
        return lines


def generate_tree_from_rule_str(rule_str, grammar):
    try:
        rules = [int(rule) for rule in rule_str.split()]
        hyp = Hypothesis(grammar)
        for rule_id in rules:
            c_rule = grammar.id_to_rule[rule_id]
            hyp.apply_rule(c_rule)
        return hyp.tree
    except:
        return None


def generate_terminal_node_sequence(rule_str, grammar):
    try:
        rules = [int(rule) for rule in rule_str.split()]
        hyp = Hypothesis(grammar)
        for rule_id in rules:
            c_rule = grammar.id_to_rule[rule_id]
            hyp.apply_rule(c_rule)
        return hyp.get_terminal_sequence()
    except:
        return None


def get_tree_edit_distance(tree1, tree2):
    class TreeEditDistanceConfig(Config):
        def __init__(self):
            pass

        def rename(self, node1, node2):
            return 1 if node1.value != node2.value else 0

        def children(self, node):
            return [x for x in node.children]

    apted = APTED(tree1, tree2, TreeEditDistanceConfig())
    ed = apted.compute_edit_distance()
    return ed


if __name__ == '__main__':
    debug('hello')
