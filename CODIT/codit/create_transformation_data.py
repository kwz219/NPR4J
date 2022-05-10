import argparse
import os
import pickle

import numpy
import numpy as np

from codit.grammar import ASTNode, get_grammar
from util import debug


def serialize_to_file(obj, path, protocol=pickle.HIGHEST_PROTOCOL):
    f = open(path, 'wb')
    pickle.dump(obj, f, protocol=protocol)
    f.close()


def deserialize_from_file(path):
    f = open(path, 'rb')
    obj = pickle.load(f)
    f.close()
    return obj


def read_code_from_file(file):
    codes = []
    with open(file) as fp:
        for line in fp:
            codes.append(line.strip())
    return codes


def read_binary_tree_string_from_file(file):
    trees = []
    with open(file) as fp:
        for line in fp:
            trees.append(line.strip())
    return trees


value_nodes = []


def fix_ast(root):
    if isinstance(root, ASTNode):
        if root.is_leaf:
            if root.value == '?':
                root.type = '900'
            if root.value == '<EMPTY>':
                root.type = '901'
                root.value = '{}'
            return
        elif len(root.children) == 1 and root.children[0].is_leaf:
            child_value = root.children[0].type
            root.value = child_value
            root.children = []
            fix_ast(root)
        else:
            for child in root.children:
                fix_ast(child)


def create_tree_from_string(line):
    tokens = line.strip().split(' ')
    stack = []
    for token in tokens:
        token = token.strip()
        if token == '':
            continue
        if token == '`':
            stack.append(token)
        elif token == '``':
            children = []
            top_of_stack = stack.pop()
            while top_of_stack != '`' and len(stack) != 0:
                children.append(top_of_stack)
                top_of_stack = stack.pop()
            top_of_stack = stack.pop()
            if isinstance(top_of_stack, ASTNode):
                for child in children:
                    top_of_stack.add_child(child)
            stack.append(top_of_stack)
        else:
            node = ASTNode(token)
            stack.append(node)
    root = stack.pop()
    fix_ast(root)
    lstr = ' '.join([str(leaf.value) for leaf in root.get_leaves()])
    if lstr == '{}':
        return None
    return root


def read_and_create_ast_from_file(file):
    trees = []
    with open(file) as fp:
        for line in fp:
            line = line.strip()
            # print line
            trees.append(create_tree_from_string(line))
    return trees


def get_left_most_node(node):
    assert isinstance(node, ASTNode)
    if len(node.children) != 0:
        return get_left_most_node(node.children[0])
    else:
        return node


def get_right_most_node(node):
    assert isinstance(node, ASTNode)
    if len(node.children) != 0:
        return get_right_most_node(node.children[-1])
    else:
        return node


def find_closest_right_cousin(node, tree):
    assert isinstance(node, ASTNode) and isinstance(tree, ASTNode)
    if node.parent is None:
        return None
    parent = node.parent
    number_of_siblings = len(parent.children)
    if node not in parent.children:
        return None
    ci = parent.children.index(node)
    if ci < number_of_siblings - 1:
        return get_left_most_node(parent.children[ci + 1])
    else:
        return find_closest_right_cousin(parent, tree)
    pass


def find_closest_left_cousin(node, tree):
    assert isinstance(node, ASTNode) and isinstance(tree, ASTNode)
    if node.parent is None:
        return None
    parent = node.parent
    if node not in parent.children:
        return None
    ci = parent.children.index(node)
    if ci > 0:
        return get_right_most_node(parent.children[ci - 1])
    else:
        return find_closest_left_cousin(parent, tree)
    pass


def get_identifier_type(node, tree, code):
    assert isinstance(node, ASTNode)
    left_cousin = find_closest_left_cousin(node, tree)
    right_cousin = find_closest_right_cousin(node, tree)
    if left_cousin is not None and left_cousin.value == 'new':
        return 'type'
    if right_cousin is not None:
        if right_cousin.value == '(' or right_cousin.value == '()' or right_cousin.value == '( )':
            return 'method'
        if right_cousin.value == '[' or right_cousin.value == '[]':
            return 'type'
        if right_cousin.type == '42':
            return 'type'
    pass


def classify_token(token):
    if '.' in token:
        return '40'
    first_char = token[0]
    if ord('A') <= ord(first_char) <= ord('Z'):
        return '801'
    else:
        return '800'
    pass


def pre_process_java_change_data(parent_codes, parent_trees, child_codes,
                                 child_trees, parent_tree_os, type='original', allowed_tokens=None,
                                 file_names=None):
    data = []
    if allowed_tokens is not None:
        assert len(allowed_tokens) == len(parent_codes)
    if file_names is None:
        file_names = [''] * len(parent_codes)
    for idx, (parent_code, parent_tree, child_code, child_tree, parent_tree_o, file_name) in \
            enumerate(zip(parent_codes, parent_trees, child_codes, child_trees, parent_tree_os, file_names)):
        if parent_tree is None or len(parent_tree) < 5:
            continue
        if idx % 1000 == 0:
            debug(idx)
        if allowed_tokens is not None:
            atc = dict()
            atc['40'], atc['800'], atc['801'], atc['802'] = [], [], [], []
            for token in allowed_tokens[idx]:
                atc[classify_token(token)].append(token)
        else:
            atc = dict()
            atc['40'], atc['800'], atc['801'], atc['802'] = [], [], [], []

        assert isinstance(parent_tree_o, ASTNode) and isinstance(child_tree, ASTNode)
        variables = set()
        method_names = set()
        type_names = set()
        packages = set()
        p_nodes = parent_tree_o.get_leaves()
        for node_p in p_nodes:
            if node_p.type.strip() == '42':
                ident_type = get_identifier_type(node_p, parent_tree_o, parent_code)
                if ident_type == 'method':
                    method_names.add(node_p.value.strip())
                elif ident_type == 'type':
                    type_names.add(node_p.value.strip())
                else:
                    variables.add(node_p.value.strip())
            elif node_p.type.strip() == '40':
                packages.add(node_p.value.strip())

        c_nodes = child_tree.get_leaves()
        for node_c in c_nodes:
            child_value = node_c.value.strip()
            if node_c.type.strip() == '42':
                ident_type = get_identifier_type(node_c, child_tree, child_code)
                if ident_type == 'method':
                    method_names.add(child_value)
                elif ident_type == 'type':
                    type_names.add(child_value)
                else:
                    variables.add(child_value)
            elif node_c.type.strip() == '40':
                packages.add(child_value)

        variable_map = {}
        for id1, v in enumerate(variables):
            variable_map[v] = "VAR_" + str(id1 + 1)
        method_name_map = {}
        for id1, v in enumerate(method_names):
            method_name_map[v] = "METHOD_" + str(id1 + 1)
        type_map = {}
        for id1, v in enumerate(type_names):
            type_map[v] = "TYPE_" + str(id1 + 1)
        package_map = {}
        for id1, v in enumerate(packages):
            package_map[v] = "PACKAGE_" + str(id1 + 1)

        for np in p_nodes:
            if np.type.strip() == '40' or np.type.strip() == '42':
                v = np.value.strip()
                if v in variable_map.keys():
                    np.type = '800'
                    if type == 'abstract':
                        np.value = variable_map[v]
                    if v in atc['800']:
                        atc['800'].remove(v)
                    atc['800'].append(np.value)
                elif v in type_map.keys():
                    np.type = '801'
                    if type == 'abstract':
                        np.value = type_map[v]
                    if v in atc['801']:
                        atc['801'].remove(v)
                    atc['801'].append(np.value)
                elif v in method_name_map.keys():
                    np.type = '802'
                    if type == 'abstract':
                        np.value = method_name_map[v]
                    if v in atc['802']:
                        atc['802'].remove(v)
                    atc['802'].append(np.value)
                elif v in package_map.keys():
                    if type == 'abstract':
                        np.value = package_map[v]
                    if v in atc['40']:
                        atc['40'].remove(v)
                    atc['40'].append(np.value)

        if type == 'abstract':
            parent_code = ' '.join([str(pn.value) for pn in parent_tree_o.get_leaves()])
            parent_code_abstract = parent_code
        else:
            _code_abstract = []
            for pn in parent_tree_o.get_leaves():
                if pn.value in variable_map.keys():
                    _code_abstract.append(variable_map[pn.value])
                elif pn.value in type_map.keys():
                    _code_abstract.append(type_map[pn.value])
                elif pn.value in method_name_map.keys():
                    _code_abstract.append(method_name_map[pn.value])
                elif pn.value in package_map.keys():
                    _code_abstract.append(package_map[pn.value])
                else:
                    _code_abstract.append(pn.value)
            parent_code_abstract = ' '.join(_code_abstract)

        for nc in c_nodes:
            if nc.type.strip() == '40' or nc.type.strip() == '42':
                v = nc.value.strip()
                if v in variable_map.keys():
                    nc.type = '800'
                    if type == 'abstract':
                        nc.value = variable_map[v]
                elif v in type_map.keys():
                    nc.type = '801'
                    if type == 'abstract':
                        nc.value = type_map[v]
                elif v in method_name_map.keys():
                    nc.type = '802'
                    if type == 'abstract':
                        nc.value = method_name_map[v]
                elif v in package_map.keys():
                    if type == 'abstract':
                        nc.value = package_map[v]

        if type == 'abstract':
            child_code = ' '.join([str(cn.value) for cn in child_tree.get_leaves()])
            child_code_abstract = child_code
        else:
            _code_abstract = []
            for pn in child_tree.get_leaves():
                if pn.value in variable_map.keys():
                    _code_abstract.append(variable_map[pn.value])
                elif pn.value in type_map.keys():
                    _code_abstract.append(type_map[pn.value])
                elif pn.value in method_name_map.keys():
                    _code_abstract.append(method_name_map[pn.value])
                elif pn.value in package_map.keys():
                    _code_abstract.append(package_map[pn.value])
                else:
                    _code_abstract.append(pn.value)
            child_code_abstract = ' '.join(_code_abstract)

        nodes = ['40', '800', '801', '802']
        for node in nodes:
            atc[node] = list(set(atc[node]))

        example = {'id': idx, 'query_tokens': parent_code.split(), 'code': child_code,
                   'parent_tree': parent_tree, 'child_tree': child_tree,
                   'parent_original_tree': parent_tree_o, 'atc': atc,
                   'file_name': file_name, 'parent_code_abstract': parent_code_abstract,
                   'child_code_abstract': child_code_abstract
                   }

        data.append(example)

    return data


# helper function begins
def get_terminal_tokens(_terminal_str):
    return [_terminal_str.strip()]


def read_raw_data(p_code, p_tree, c_code, c_tree, parent_original_tree,
                  allowed_tokens_file, file_names_file, exc_str_ch=True, samples=10000000):
    pc = open(p_code)
    pt = open(p_tree)
    cc = open(c_code)
    ct = open(c_tree)
    pot = open(parent_original_tree)
    ats = open(allowed_tokens_file)
    fnf = None
    if os.path.exists(file_names_file):
        fnf = open(file_names_file)

    included_ids = []
    pcodes = []
    ptrees = []
    ccodes = []
    ctrees = []
    potrees = []
    allowed_tokens = []
    file_names = []
    if fnf is None:
        counter = 0
        for idx, (pcs, pts, ccs, cts, pots, at) in enumerate(zip(pc, pt, cc, ct, pot, ats)):
            if exc_str_ch and cts.strip() == pots.strip():
                continue
            if '`' in ccs:
                continue
            if len(pts.strip()) < 5:
                continue
            ct = create_tree_from_string(cts)
            pot = create_tree_from_string(pots)
            if ct is None or pot is None:
                continue
            counter += 1
            pcodes.append(pcs.strip())
            ptrees.append(pts.strip())
            ccodes.append(ccs.strip())
            ctrees.append(ct)
            potrees.append(pot)
            allowed = [s.strip() for s in at.split()]
            allowed_tokens.append(allowed)
            # print(allowed_tokens[-1])
            included_ids.append(idx)
            if counter == samples:
                break
        file_names = [None] * len(pcodes)
    else:
        counter = 0
        for idx, (pcs, pts, ccs, cts, pots, at, fn) in enumerate(zip(pc, pt, cc, ct, pot, ats, fnf)):
            if exc_str_ch and pcs.strip() == ccs.strip():
                continue
            if '`' in ccs:
                continue
            if len(pts.strip()) < 5:
                continue
            ct = create_tree_from_string(cts)
            pot = create_tree_from_string(pots)
            if ct is None or pot is None:
                continue
            counter += 1
            pcodes.append(pcs.strip())
            ptrees.append(pts.strip())
            ccodes.append(ccs.strip())
            ctrees.append(ct)
            potrees.append(pot)
            allowed = [s.strip() for s in at.split()]
            allowed_tokens.append(allowed)
            # print(allowed_tokens[-1])
            file_names.append(fn)
            included_ids.append(idx)
            if counter == samples:
                break
    return pcodes[:samples], ptrees[:samples], ccodes[:samples], \
           ctrees[:samples], potrees[:samples], allowed_tokens[:samples], file_names[:samples], included_ids[:samples]


def get_final_token_mask(allowed_tokens, t_vocab):
    indices = []
    for word in allowed_tokens:
        if word in t_vocab.token_id_map.keys():
            indices.append(t_vocab.token_id_map[word])
        else:
            if word.strip() in t_vocab.token_id_map.keys():
                indices.append(t_vocab.token_id_map[word.strip()])
    mask = numpy.array([1e-30] * t_vocab.size, dtype='float32')
    for index in indices:
        mask[index] = 1.00
    # print np.sum(mask)
    return numpy.array(indices), mask
    pass


def read_train_and_test_data(train_folders, valid_folder, test_folder):
    parent_codes = []
    parent_trees = []
    child_codes = []
    child_trees = []
    parent_tree_o = []
    allowed_tokens_all = []
    train_ids = []
    file_names = []
    valid_ids = []
    for train_folder in train_folders:
        parent_version_code_file = train_folder + '/parent.code'
        parent_version_tree_file = train_folder + '/parent.tree'
        child_version_code_file = train_folder + '/child.code'
        child_version_tree_file = train_folder + '/child.tree'
        parent_original_tree_file = train_folder + '/parent.org.tree'
        allowed_tokens_file_name = train_folder + '/allowed.tokens'
        file_names_file = train_folder + '/files.txt'
        parent_codes_train, parent_trees_train, child_codes_train, child_trees_train, \
        parent_tree_o_train, allowed_tokens_train, file_names_all, all_ids_train = read_raw_data(
            parent_version_code_file,
            parent_version_tree_file,
            child_version_code_file,
            child_version_tree_file,
            parent_original_tree_file,
            allowed_tokens_file_name,
            file_names_file,
            True
        )
        parent_codes.extend(parent_codes_train)
        parent_trees.extend(parent_trees_train)
        child_codes.extend(child_codes_train)
        child_trees.extend(child_trees_train)
        parent_tree_o.extend(parent_tree_o_train)
        allowed_tokens_all.extend(allowed_tokens_train)
        file_names.extend(file_names_all)
        train_ids.extend(all_ids_train)

    parent_version_code_file = valid_folder + '/parent.code'
    parent_version_tree_file = valid_folder + '/parent.tree'
    child_version_code_file = valid_folder + '/child.code'
    child_version_tree_file = valid_folder + '/child.tree'
    parent_original_tree_file = valid_folder + '/parent.org.tree'
    allowed_tokens_file_name = valid_folder + '/allowed.tokens'
    file_names_file = valid_folder + '/files.txt'
    parent_codes_test, parent_trees_test, child_codes_test, child_trees_test, \
    parent_tree_o_test, allowed_tokens_test, file_names_all, all_ids_test = read_raw_data(
        parent_version_code_file,
        parent_version_tree_file,
        child_version_code_file,
        child_version_tree_file,
        parent_original_tree_file,
        allowed_tokens_file_name,
        file_names_file,
        True
    )
    parent_codes.extend(parent_codes_test)
    parent_trees.extend(parent_trees_test)
    child_codes.extend(child_codes_test)
    child_trees.extend(child_trees_test)
    parent_tree_o.extend(parent_tree_o_test)
    allowed_tokens_all.extend(allowed_tokens_test)
    file_names.extend(file_names_all)
    valid_ids.extend(all_ids_test)

    parent_version_code_file = test_folder + '/parent.code'
    parent_version_tree_file = test_folder + '/parent.tree'
    child_version_code_file = test_folder + '/child.code'
    child_version_tree_file = test_folder + '/child.tree'
    parent_original_tree_file = test_folder + '/parent.org.tree'
    allowed_tokens_file_name = test_folder + '/allowed.tokens'
    file_names_file = test_folder + '/files.txt'
    parent_codes_test, parent_trees_test, child_codes_test, child_trees_test, \
    parent_tree_o_test, allowed_tokens_test, file_names_all, all_ids_test = read_raw_data(
        parent_version_code_file,
        parent_version_tree_file,
        child_version_code_file,
        child_version_tree_file,
        parent_original_tree_file,
        allowed_tokens_file_name,
        file_names_file,
        True
    )
    parent_codes.extend(parent_codes_test)
    parent_trees.extend(parent_trees_test)
    child_codes.extend(child_codes_test)
    child_trees.extend(child_trees_test)
    parent_tree_o.extend(parent_tree_o_test)
    allowed_tokens_all.extend(allowed_tokens_test)
    file_names.extend(file_names_all)
    return parent_codes, parent_trees, child_codes, child_trees, parent_tree_o, \
           allowed_tokens_all, file_names, len(train_ids), len(valid_ids)


def create_all_files(folder_name, data_type):
    if not os.path.exists(folder_name + '/' + data_type):
        os.mkdir(folder_name + '/' + data_type)
    prev_rule_file = open(os.path.join(folder_name + '/' + data_type, 'prev.rule'), 'w')
    next_rule_file = open(os.path.join(folder_name + '/' + data_type, 'next.rule'), 'w')
    prev_rule_parent_file = open(os.path.join(folder_name + '/' + data_type, 'prev.parent.rule'), 'w')
    next_rule_parent_file = open(os.path.join(folder_name + '/' + data_type, 'next.parent.rule'), 'w')
    prev_rule_parent_t_file = open(os.path.join(folder_name + '/' + data_type, 'prev.parent.time'), 'w')
    next_rule_parent_t_file = open(os.path.join(folder_name + '/' + data_type, 'next.parent.time'), 'w')
    prev_token_node_id_file = open(os.path.join(folder_name + '/' + data_type, 'prev.token.id'), 'w')
    next_token_node_id_file = open(os.path.join(folder_name + '/' + data_type, 'next.token.id'), 'w')
    prev_token_file = open(os.path.join(folder_name + '/' + data_type, 'prev.token'), 'w')
    next_token_file = open(os.path.join(folder_name + '/' + data_type, 'next.token'), 'w')
    prev_token_plus_id_file = open(os.path.join(folder_name + '/' + data_type, 'prev.augmented.token'), 'w')
    next_token_plus_id_file = open(os.path.join(folder_name + '/' + data_type, 'next.augmented.token'), 'w')
    prev_augmented_rule_file = open(os.path.join(folder_name + '/' + data_type, 'prev.augmented.rule'), 'w')
    next_augmented_rule_file = open(os.path.join(folder_name + '/' + data_type, 'next.augmented.rule'), 'w')
    prev_frontier_file = open(os.path.join(folder_name + '/' + data_type, 'prev.frontier'), 'w')
    next_frontier_file = open(os.path.join(folder_name + '/' + data_type, 'next.frontier'), 'w')
    parent_tree_file = open(os.path.join(folder_name + '/' + data_type, 'prev.tree'), 'w')
    child_tree_file = open(os.path.join(folder_name + '/' + data_type, 'next.tree'), 'w')
    return prev_rule_file, next_rule_file, prev_rule_parent_file, next_rule_parent_file, \
           prev_rule_parent_t_file, next_rule_parent_t_file, prev_token_node_id_file, \
           next_token_node_id_file, prev_token_file, next_token_file, prev_token_plus_id_file, \
           next_token_plus_id_file, \
           prev_augmented_rule_file, next_augmented_rule_file, prev_frontier_file, next_frontier_file, \
           parent_tree_file, child_tree_file


def write_contents(prev_rule_file, next_rule_file, prev_rule_parent_file, next_rule_parent_file,
                   prev_rule_parent_t_file, next_rule_parent_t_file, prev_token_node_id_file,
                   next_token_node_id_file, prev_token_file, next_token_file, prev_token_plus_id_file,
                   next_token_plus_id_file, prev_augmented_rule_file, next_augmented_rule_file,
                   prev_frontier_file, next_frontier_file, parent_tree_file, child_tree_file,
                   prev_rule, next_rule, prev_rule_parent, next_rule_parent,
                   prev_rule_parent_t, next_rule_parent_t, prev_token_node_id,
                   next_token_node_id, prev_token, next_token, prev_rule_frontier, next_rule_frontier,
                   parent_tree, child_tree):
    if len(prev_rule) == 0 or len(next_rule) == 0 or len(prev_token) == 0 or len(next_token) == 0 or \
            len(prev_token_node_id) == 0 or len(next_token_node_id) == 0 or len(prev_rule_frontier) == 0 or \
            len(next_rule_frontier) == 0:
        return 0

    prev_rule_file.write(' '.join([str(x) for x in prev_rule]) + '\n')
    next_rule_file.write(' '.join([str(x) for x in next_rule]) + '\n')
    prev_rule_parent_file.write(' '.join([str(x) for x in prev_rule_parent]) + '\n')
    next_rule_parent_file.write(' '.join([str(x) for x in next_rule_parent]) + '\n')
    prev_rule_parent_t_file.write(' '.join([str(x) for x in prev_rule_parent_t]) + '\n')
    next_rule_parent_t_file.write(' '.join([str(x) for x in next_rule_parent_t]) + '\n')
    prev_token_node_id_file.write(' '.join([str(x) for x in prev_token_node_id]) + '\n')
    next_token_node_id_file.write(' '.join([str(x) for x in next_token_node_id]) + '\n')
    prev_token_file.write(' '.join([str(x) for x in prev_token]) + '\n')
    next_token_file.write(' '.join([str(x) for x in next_token]) + '\n')
    ############### Do the alighment #######################
    # prev_token_node_id.append(-1)
    # next_token_node_id.append(-1)
    # prev_token_node_id = prev_token_node_id[1:]
    # next_token_node_id = next_token_node_id[1:]
    #######################################################
    prev_augmented_token_str = ' '.join([str(x) + u"|" + str(y) for x, y in zip(prev_token, prev_token_node_id)]) + '\n'
    next_augmented_token_str = ' '.join([str(x) + u"|" + str(y) for x, y in zip(next_token, next_token_node_id)]) + '\n'
    prev_token_plus_id_file.write(prev_augmented_token_str)
    next_token_plus_id_file.write(next_augmented_token_str)

    prev_frontier_file.write(' '.join([str(x) for x in prev_rule_frontier]) + '\n')
    next_frontier_file.write(' '.join([str(x) for x in next_rule_frontier]) + '\n')

    prev_rule_frontier.append(-1)
    next_rule_frontier.append(-1)
    prev_rule_frontier = prev_rule_frontier[1:]
    next_rule_frontier = next_rule_frontier[1:]
    prev_augmented_rule_str = ' '.join([str(x) + u"|" + str(y) for x, y in zip(prev_rule, prev_rule_frontier)]) + '\n'
    next_augmented_rule_str = ' '.join([str(x) + u"|" + str(y) for x, y in zip(next_rule, next_rule_frontier)]) + '\n'
    prev_augmented_rule_file.write(prev_augmented_rule_str)
    next_augmented_rule_file.write(next_augmented_rule_str)
    parent_tree_file.write(str(parent_tree) + '\n')
    child_tree_file.write(str(child_tree) + '\n')
    return 1


def flush_all(*files):
    for f in files:
        f.flush()


def close_all(*files):
    for f in files:
        f.close()


def get_token_str(example):
    prev_token_str = ' '.join(example[-8])
    next_token_str = ' '.join(example[-7])
    return prev_token_str + ' ' + next_token_str
    pass


def get_tree_productions(tree):
    assert isinstance(tree, ASTNode)
    stack = []
    # for


def check_and_remove_example_from_train_data(train_data, example):
    example_str = get_token_str(example)
    indices = []
    new_train_data = np.array(train_data)
    for idx, t_ex in enumerate(train_data):
        t_ex_str = get_token_str(t_ex)
        if example_str == t_ex_str:
            fid = idx
            indices.append(fid)
            break
    all_indices = [i for i in range(len(new_train_data))]
    for fid in indices:
        all_indices.remove(fid)
    return new_train_data[all_indices].tolist()
    pass


def already_exists(_data, example):
    examples_str = set([get_token_str(ex) for ex in _data])
    ex_str = get_token_str(example)
    return ex_str in examples_str
    pass


def parse_java_change_dataset():
    import os
    parser = argparse.ArgumentParser()

    parser.add_argument('-data', help='Main Data Directory', default='/home/saikatc/Research/codit_data/')
    parser.add_argument('-source', help='Relative path of the data source', default='complete_split_data')
    parser.add_argument('-train', help='Train Folder Name(s)', nargs='+', default=['train'])
    parser.add_argument('-valid', help='Train Folder Name', default='valid')
    parser.add_argument('-test', help='Train Folder Name(s)', default='test')

    parser.add_argument('-output', help='name of the output folder',
                        default='/home/saikatc/data_hdd/Codit/CoditData')
    parser.add_argument('-name', help='name of the data file', default='10_20_original')
    parser.add_argument('-exclude_no_structure_change', action='store_true')
    parser.add_argument('-type', help='Type of the Data given', default='concrete')
    parser.add_argument('-remove_repeat', action='store_false')

    # parser.set_defaults(exclude_string_change=True)
    args = parser.parse_args()
    debug(args)
    data_base = os.path.join(args.data, args.source)
    name = args.name
    data_directory = os.path.join(data_base, name)
    train_folders = [os.path.join(data_directory, train) for train in args.train]
    test_folder = os.path.join(data_directory, args.test)
    valid_folder = os.path.join(data_directory, args.valid)
    if not os.path.exists(args.output):
        os.mkdir(args.output)

    parent_codes, parent_trees, child_codes, child_trees, parent_tree_o, allowed_tokens_for_nodes, \
    file_names, num_train_examples, num_valid_examples \
        = read_train_and_test_data(train_folders, valid_folder, test_folder)
    total_examples = len(parent_codes)
    num_test_examples = total_examples - num_train_examples - num_valid_examples

    assert len(parent_codes) == len(parent_trees) and len(parent_codes) == len(child_codes) and \
           len(parent_codes) == len(child_trees) and len(parent_codes) == len(parent_tree_o) and \
           len(parent_codes) == len(allowed_tokens_for_nodes)

    debug('Training Examples :\t' + str(num_train_examples))
    debug('Validation Examples :\t' + str(num_valid_examples))
    debug('Test Examples :  \t' + str(num_test_examples))
    num_valid_examples += num_train_examples

    debug('Finished Reading Data')

    data = pre_process_java_change_data(parent_codes=parent_codes, parent_trees=parent_trees,
                                        child_codes=child_codes, child_trees=child_trees,
                                        parent_tree_os=parent_tree_o, type=args.type,
                                        file_names=file_names)

    pt = [entry['parent_original_tree'] for entry in data]
    pt.extend([entry['child_tree'] for entry in data])
    grammar = get_grammar(pt)
    debug('Total rules : ' + str((len(grammar.rules))))
    debug(grammar.terminal_nodes)
    value_nodes = grammar.value_node_rules.keys()
    debug('Total Value Nodes : ', len(value_nodes))
    train_data, dev_data, test_data, all_examples, train_ids, dev_ids, test_ids = [], [], [], [], [], [], []

    for idx, entry in enumerate(data):
        if idx % 1000 == 0:
            debug(idx)
        prev_token_node_id, prev_token, next_token_node_id, next_token, next_rule, next_rule_parent_t, \
        next_rule_parent, prev_rule, prev_rule_parent, prev_rule_parent_t, \
        prev_rule_frontier, next_rule_frontier = [], [], [], [], [], [], [], [], [], [], [], []

        parse_tree = entry['child_tree']
        parent_original_tree = entry['parent_original_tree']

        rule_list_next_v, rule_parents_next_v, value_nodes_next_v = parse_tree.get_productions(include_value_node=True)
        rule_list_prev_v, rule_parents_prev_v, value_nodes_prev_v = parent_original_tree.get_productions(
            include_value_node=True)
        actions = []
        rule_pos_map = dict()
        action_list_prev = []
        for rule_count, rule in enumerate(rule_list_next_v):
            if not grammar.is_value_node(rule):
                parent_rule = rule_parents_next_v[(rule_count, rule)][0]
                if parent_rule:
                    parent_t = rule_pos_map[parent_rule]
                else:
                    parent_t = 0
                rule_pos_map[rule] = len(actions)
                action = 'Action(APPLY_RULE, d)'
                actions.append(action)
                rid = grammar.rule_to_id.get(rule)
                if rid is None:
                    print(rule)
                action_list_prev.append('A.' + str(rid))
                next_rule.append(rid)
                next_rule_parent_t.append(grammar.rule_to_id.get(parent_rule))
                next_rule_parent.append(parent_t)
                next_rule_frontier.append(rule.type)
            else:
                v = rule.value
                if v == '|':
                    v = 'BIT_OR'
                elif v == '||':
                    v = 'LOG_OR'
                action_list_prev.append('G.' + str(v))
                node_id = str(rule.type)
                node_value = str(rule.value)
                next_token_node_id.append(node_id)
                next_token.append(node_value)

        actions = []
        action_list_n = []
        rule_pos_map = dict()
        for rule_count, rule in enumerate(rule_list_prev_v):
            if not grammar.is_value_node(rule):
                parent_rule = rule_parents_prev_v[(rule_count, rule)][0]
                if parent_rule:
                    parent_t = rule_pos_map[parent_rule]
                else:
                    parent_t = 0
                rule_pos_map[rule] = len(actions)
                action = 'Action(APPLY_RULE, d)'
                actions.append(action)
                rid = grammar.rule_to_id.get(rule)
                if rid is None:
                    print(rule)
                action_list_n.append('A.' + str(rid))
                prev_rule.append(rid)
                prev_rule_parent.append(grammar.rule_to_id.get(parent_rule))
                prev_rule_parent_t.append(parent_t)
                prev_rule_frontier.append(rule.type)
            else:
                node_id = str(rule.type)
                node_value = str(rule.value)
                prev_token_node_id.append(node_id)
                prev_token.append(node_value)
                v = rule.value
                if v == '|':
                    v = 'BIT_OR'
                elif v == '||':
                    v = 'LOG_OR'
                action_list_n.append('G.' + str(v))

        if args.exclude_no_structure_change and prev_rule == next_rule:
            continue
        atc = entry['atc']
        example = [
            action_list_prev, action_list_n, entry['parent_code_abstract'], entry['child_code_abstract'],
            prev_rule, next_rule, prev_rule_parent, next_rule_parent,
            prev_rule_parent_t, next_rule_parent_t, prev_token_node_id,
            next_token_node_id, prev_token, next_token, prev_rule_frontier, next_rule_frontier,
            parent_original_tree, parse_tree, atc, entry['file_name'],
        ]
        all_examples.append(example)

        if idx < num_train_examples:
            if not already_exists(train_data, example):
                train_data.append(example)
                train_ids.append(idx)
        elif idx < num_valid_examples:
            if args.remove_repeat:
                check_and_remove_example_from_train_data(train_data, example)
            if not already_exists(dev_data, example):
                dev_data.append(example)
                dev_ids.append(idx)
        else:
            if args.remove_repeat:
                train_data = check_and_remove_example_from_train_data(train_data, example)
            if not already_exists(test_data, example):
                test_data.append(example)
                test_ids.append(idx)
    atc_file_name = 'atc_scope.bin'
    train_w = write_all_content_to_file(args, atc_file_name, train_data, 'train')
    valid_w = write_all_content_to_file(args, atc_file_name, dev_data, 'valid')
    test_w = write_all_content_to_file(args, atc_file_name, test_data, 'test')
    debug(train_w, valid_w, test_w)
    serialize_to_file(grammar, os.path.join(args.output, 'grammar.bin'))
    return train_data, dev_data, test_data


def write_all_content_to_file(args, atc_file_name, _data, name):
    _file_all = create_all_files(args.output, name)
    train_w = 0
    _atc = []
    file_names_file = open(os.path.join(args.output, name + '/files.txt'), 'w')
    parent_abstract_file = open(os.path.join(args.output, name + '/prev.abstract.code'), 'w')
    child_abstract_file = open(os.path.join(args.output, name + '/next.abstract.code'), 'w')
    parent_actions = open(os.path.join(args.output, name + '/prev.actions'), 'w')
    child_actions = open(os.path.join(args.output, name + '/next.actions'), 'w')
    for ex in _data:
        af = [f for f in _file_all]
        af.extend(ex[4:-2])
        _atc.append(ex[-2])
        success = write_contents(*af)
        train_w += success
        flush_all(*_file_all)
        if success == 1:
            file_names_file.write(ex[-1].strip() + '\n')
            parent_actions.write(' '.join(ex[0]) + '\n')
            child_actions.write(' '.join(ex[1]) + '\n')
            parent_abstract_file.write(ex[2] + '\n')
            child_abstract_file.write(ex[3] + '\n')
    file_names_file.close()
    parent_abstract_file.close()
    child_abstract_file.close()
    parent_actions.close()
    child_actions.close()
    atc_file = os.path.join(args.output, name + '/' + atc_file_name)
    serialize_to_file(_atc, atc_file)
    close_all(*_file_all)
    return train_w


if __name__ == '__main__':
    parse_java_change_dataset()
