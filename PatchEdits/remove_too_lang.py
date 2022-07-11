import os
from tqdm import tqdm
import argparse


arg = argparse.ArgumentParser()
arg.add_argument("--length", type=int, help="max length of sentence")
arg.add_argument("--path", type=str, help="old_path", default='my_data/my_data.txt')
arg.add_argument("--new_path", type=str, help="new path", default='my_data/my_data_new.txt')
arg = arg.parse_args()

new_data = []
with open(arg.path, encoding='utf-8') as fp:
    for line in tqdm(fp):
        if len(line.split()) <= arg.length:
            new_data.append(line)

with open(arg.new_path, 'w', encoding='utf-8') as fp:
    for line in tqdm(new_data):
        fp.write(line)
