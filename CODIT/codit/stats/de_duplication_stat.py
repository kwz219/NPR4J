import sys, os
import nltk
import numpy as np

class Patch():
    def __init__(self):
        self.id = -1
        self.parent_code = ''
        self.child_code = ''
        self.patches = []
        self.verdict = False
        self.distance = 0
        self.verdict_token = False
        pass

    def __repr__(self):
        return str(self.id) + '\n' + ' '.join(self.parent_code) + '\n' + ' '.join(self.child_code) \
               + '\n' + str(self.distance) + '\n' + str(self.verdict)


def read_patch(file_path, size):
    num_line_per_patch = size * 2 + 9
    patches_lines = []
    with open(file_path) as f:
        patch = []
        for ln, line in enumerate(f):
            line = line.strip()
            if (ln % num_line_per_patch == 0) and (ln != 0):
                patches_lines.append([l for l in patch])
                patch = []
            patch.append(line)
        patches_lines.append(patch)

    patches = []
    for lines in patches_lines:
        ex = Patch()
        ex.id = int(lines[0])
        ex.parent_code = [token.strip() for token in lines[1].split()]
        ex.child_code = [token.strip() for token in lines[3].split()]
        ex.patches = []
        for gen_idx in range(size):
            cidx = gen_idx * 2
            didx = cidx + 1
            ex.patches.append([lines[cidx + 7], int(lines[didx + 7])])
        verdict = lines[-2].strip()
        if verdict == 'True':
            ex.verdict = True
        else:
            ex.verdict = False
        # print(verdict)
        ex.distance = nltk.edit_distance([token.strip() for token in ex.parent_code],
                                         [token.strip() for token in ex.child_code])
        patches.append(ex)
    return np.asarray(patches)


def de_duplicate_patches(patches):
    patch_map = {}
    for pidx, patch in enumerate(patches):
        key = ' '.join(patch.parent_code) + ' '.join(patch.child_code)
        if key not in patch_map.keys():
            patch_map[key] = []
        patch_map[key].append([patch, pidx])
    unique_indices = []
    for key in patch_map:
        ps = patch_map[key]
        if len(ps) == 1:
            unique_indices.append(ps[0][1])
        else:
            idx = -1
            for pi, p in enumerate(ps):
                if p[0].verdict:
                    idx = pi
            unique_indices.append(ps[idx][1])
    return unique_indices
    pass


if __name__ == '__main__':
    result_base = '/home/sc2nf/codit-clone'
    option = 'token' # 'token
    size = 10
    # if option == 'tree':
    #     file_name = 'codit-all-concrete_' + str(size) + '.2_' + str(2*size) + '_decode_res.txt'
    # else:
    #     file_name = 'codit.all.token.top.' + str(size) + '_' + str(size) + '_decode_res.txt'

    file_name_tree = 'codit-all-concrete_' + str(size) + '.2_' + str(2 * size) + '_decode_res.txt'
    file_path_tree = result_base + '/' + file_name_tree
    patches_tree = read_patch(file_path_tree, size)
    unique_indices = de_duplicate_patches(patches_tree)
    # unique_patches_tree = patches_tree[unique_indices]
    # unique_count = len(unique_patches_tree)

    file_name_token = 'codit.all.token.top.' + str(size) + '_' + str(size) + '_decode_res.txt'
    file_path_token = result_base + '/' + file_name_token
    patches_token = read_patch(file_path_token, size)
    # unique_patches = patches_token[unique_indices]
    unified_patches = []
    for idx, (p_tree, p_token) in enumerate(zip(patches_tree, patches_token)):
        if idx in unique_indices:
            assert isinstance(p_tree, Patch) and isinstance(p_token, Patch)
            p_tree.verdict_token = p_token.verdict
            unified_patches.append(p_tree)

    tree_count = np.sum([1 if p.verdict else 0 for p in unified_patches])
    token_count = np.sum([1 if p.verdict_token else 0 for p in unified_patches])

    tree_indices = set()
    token_indices = set()
    for i, p in enumerate(unified_patches):
        if p.verdict:
            tree_indices.add(i)
        if p.verdict_token:
            token_indices.add(i)

    only_tree = tree_indices.difference(token_indices)
    only_token = token_indices.difference(tree_indices)
    common = tree_indices.intersection(token_indices)
    print(tree_count, token_count, len(only_token), len(only_tree), len(common), len(unified_patches))

    #
    # total_success_tree = np.sum([1 if p.verdict else 0 for p in unique_patches])
    # print(unique_patches, total_success_tree)
    # tree_success_indices_in_unique = set()
    # for idx, p in enumerate(unique_patches):
    #     if p.verdict:
    #         tree_success_indices_in_unique.add(idx)
    #
    #
    #
    # total_success_token = np.sum([1 if p.verdict else 0 for p in unique_patches])
    # print(tree_count, total_success_token)
