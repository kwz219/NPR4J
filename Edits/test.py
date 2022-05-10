import argparse
from tqdm import tqdm

if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument("line", type=int, help="File with pre-processed data (optional)")
    arg.add_argument("--length", type=int, help="File with pre-processed data (optional)", default=100)
    arg = arg.parse_args()

    with open('./my_data/temp_data.txt', encoding='utf-8') as fp:
        data = fp.readlines()

    left = max(0, arg.line-arg.length)
    right = min(len(data)-1, arg.line+arg.length)

    with open('./my_data/temp_data.txt', 'w', encoding='utf-8') as fp:
        for i, line in enumerate(tqdm(data)):
            if i < left or i > right:
                fp.write(line)