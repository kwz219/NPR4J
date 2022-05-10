import os
import json

words = set()
def create_tree_representation(tree_dict):
    returns = []
    stack = [tree_dict]
    while len(stack) != 0:
        node = stack.pop()
        returns.append(str(node['type']))
        returns.append('(')
        children = node['children']
        if len(children) == 0:
            words.add(str(node['value']))
            returns.append(str(node['value']))
        else:
            for child in children[::-1]:
                returns.extend(create_tree_representation(child))
        returns.append(')')
        returns.append(str(node['type']))
    return returns
    pass


if __name__ == '__main__':
    base_dir = '../data/raw/'
    parts = ['train', 'valid', 'test']
    for dataset in ['pull_request_data', 'code_change_data']:
        words = set()
        for part in parts:
            print(os.path.join(base_dir, dataset, part, 'prev.tree'))
            input_file = open(os.path.join(base_dir, dataset, part, 'prev.tree'))
            output_file = open(os.path.join(base_dir, dataset, part, 'prev.sbt'), 'w')
            for line in input_file:
                tree = json.loads(line.strip())
                output_file.write(' '.join(create_tree_representation(tree)) + '\n')
            input_file.close()
            output_file.close()
            print(os.path.join(base_dir, dataset, part, 'next.tree'))
            input_file = open(os.path.join(base_dir, dataset, part, 'next.tree'))
            output_file = open(os.path.join(base_dir, dataset, part, 'next.sbt'), 'w')
            for line in input_file:
                tree = json.loads(line.strip())
                output_file.write(' '.join(create_tree_representation(tree)) + '\n')
            input_file.close()
            output_file.close()
        print(len(words))
        print('=' * 100)