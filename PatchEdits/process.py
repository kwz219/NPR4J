import os
import re
import json
from tqdm import tqdm
import javalang

class Processor:
    def __init__(self):
        self.start_bug = "<START_BUG>"
        self.end_bug = "<END_BUG>"

    def my_open(self, file_path, encoding):
        with open(file_path, encoding=encoding) as fp:
            return fp.readlines()

    def is_junk(self, char):
        num = ord(char)
        if char < 31:
            if not char == 10:
                return True
        return False

    def deal_control_char(self, s):
        temp = re.sub('[\x00-\x09|\x0b-\x0c|\x0e-\x1f]', '', s)
        return temp

    def process(self, raw_data_path, dataset, data_path, id_path, encoding='utf-8'):
        #data_path = os.path.join(data_path, 'data.txt')
        buggy = dataset + '.buggy'
        buggy = os.path.join(raw_data_path, buggy)
        fix = dataset + '.fix'
        fix = os.path.join(raw_data_path, fix)
        ids = dataset + '.ids'
        ids = os.path.join(raw_data_path, ids)
        buggy_list = self.my_open(buggy, encoding)
        fix_list = self.my_open(fix, encoding)
        id_list = self.my_open(ids, encoding)
        count = 0

        for i, code in enumerate(tqdm(buggy_list)):
            if not (self.start_bug in code and self.end_bug in code):
                continue
            fix_code = fix_list[i].strip()
            code = self.deal_control_char(code)
            fix_code = self.deal_control_char(fix_code)
            while '###' in code:
                code = code.replace('###', '')
            while '###' in fix_code:
                fix_code = fix_code.replace('###', '')

            temp = code
            code = code.strip().split()
            start_index = code.index(self.start_bug)
            code.remove(self.start_bug)
            end_index = code.index(self.end_bug)
            code.remove(self.end_bug)

            dataset = 'test'
            data = f"{dataset} ### {' '.join(code)} ### {start_index} {end_index} ### <s> {fix_code} </s>\n"
            if data.count('###') != 3:
                print(data.count('###'), '###'in data, temp)
                print(data)
            with open(data_path, 'a', encoding=encoding) as fp:
                fp.write(data)
                count += 1
            with open(id_path, 'a', encoding=encoding) as fp:
                fp.write(id_list[i])
                count += 1
        print(buggy, count)

if __name__ == '__main__':

    datasets = ['trn', 'val', 'test']
    datasets = ['diversity']
    for dataset in datasets:
        processor = Processor()
        raw_data_path = r'F:\workspace\bug_detection\data\For_evaluation_Benchmark\Edit'
        #dataset = 'trn'
        data_path = rf'F:\workspace\bug_detection\data\For_evaluation_Benchmark\Edit\{dataset}_data.txt'
        id_path = rf'F:\workspace\bug_detection\data\For_evaluation_Benchmark\Edit\{dataset}_id.txt'
        processor.process(raw_data_path, dataset, data_path, id_path)





