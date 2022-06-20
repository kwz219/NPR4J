import nltk
import numpy as np
import os

from CODIT.translate_token import print_bleu_res_to_file


def transform_to_ngram(code, n=2):
    if len(code) <= n:
        return set([' '.join(code)])
    n_grams = []
    for i in range(-n+1, len(code) - n - 1):
        ng = []
        for j in range(n):
            if i+j < 0:
                ng.append('*')
            else:
                ng.append(code[i+j])
        n_grams.append(' '.join(ng))
    return set(n_grams)


def jaccard_dist(test_code, train_code):
    tc = transform_to_ngram(test_code)
    trc = transform_to_ngram(train_code)
    try:
        return nltk.jaccard_distance(tc, trc)
    except:
        print(test_code)
        print(train_code)
        exit()


def edit_distance(test_code, train_code):
    return nltk.edit_distance(test_code, train_code)


def sort_based_on_edit_distance(test_code, train_data):
    scores = [jaccard_dist(test_code, train_code) for train_code in train_data]
    indices = np.argsort(scores)
    scores = np.sort(scores)
    return scores, indices
    pass


def main(augmented_src_file, augmented_tgt_file, train_src_file, train_tgt_file, n_best, exp_name):
    train_src_code = []
    train_tgt_code = []
    test_data = []
    tmp_file_name = 'tmp/' + exp_name
    tfile = open(tmp_file_name, 'w')

    with open(augmented_src_file) as test_src:
        with open(augmented_tgt_file) as test_tgt:
            for idx, (src_line, tgt_line) in enumerate(zip(test_src, test_tgt)):
                src_aug_parts = src_line.strip().split()
                tgt_aug_parts = tgt_line.strip().split()
                src_parts = [parts.split(u"|")[0] for parts in src_aug_parts]
                tgt_parts = [parts.split(u"|")[0] for parts in tgt_aug_parts]
                test_data.append([src_parts, tgt_parts])

    with open(train_src_file) as train_src:
        with open(train_tgt_file) as train_tgt:
            for idx, (src_line, tgt_line) in enumerate(zip(train_src, train_tgt)):
                src_parts = [token.strip() for token in src_line.strip().split()]
                tgt_parts = [token.strip() for token in tgt_line.strip().split()]
                if len(src_parts) == 0 or len(tgt_parts) == 0:
                    continue
                train_src_code.append(src_parts)
                train_tgt_code.append(tgt_parts)

    train_src_code = np.array(train_src_code)
    train_tgt_code = np.array(train_tgt_code)
    correct = 0
    no_change = 0
    if not os.path.exists('results'):
        os.mkdir('results')

    if not os.path.exists('result_eds'):
        os.mkdir('result_eds')

    decode_res_file = open('results/' + exp_name + '_' + str(n_best) + '_decode_res.txt', 'w')
    bleu_file = open('result_eds/' + exp_name + '_' + str(n_best) + '_bleus.csv', 'w')

    all_eds = []
    total_example = 0

    for idx, (src, tgt) in enumerate(test_data):
        print('Current Example : ', idx)
        distances, indices = sort_based_on_edit_distance(src, train_src_code)

        tfile.write(', '.join([str(index) for index in indices]) + '\n')
        cand_indices = indices[:n_best]
        cands = train_tgt_code[cand_indices]
        scores = [jaccard_dist(tgt, cand) for cand in cands]
        total_example += 1
        src = ' '.join(src)
        tgt = ' '.join(tgt)
        decode_res_file.write(str(idx) + '\n')
        decode_res_file.write(src + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        decode_res_file.write(tgt + '\n')
        if src == tgt:
            no_change += 1
        decode_res_file.write('=====================================================================================\n')
        decode_res_file.write('Canditdate Size : ' + str(len(cands)) + '\n')
        decode_res_file.write('-------------------------------------------------------------------------------------\n')
        eds = []
        found = False

        for cand, ed in zip(cands, scores):
            if cand == tgt:
                found = True
            eds.append(ed)
            decode_res_file.write(' '.join(cand) + '\n')
            decode_res_file.write(str(ed) + '\n')
        if found:
            print('Correct')
            correct += 1
        all_eds.append(eds)
        decode_res_file.write(str(found) + '\n\n')
        decode_res_file.flush()
        # if idx == 20:
        #     break

    tfile.close()
    all_eds = np.asarray(all_eds)
    print_bleu_res_to_file(bleu_file, all_eds)
    decode_res_file.close()
    bleu_file.close()
    print(correct, no_change, total_example)

    pass


if __name__ == '__main__':
    s1 = 'This is a serious competetion, I should try to win!'.split()
    s2 = 'This is a serious hellp, I should try to win!'.split()
    s3 = 'This is a serious hellp, My should try to win!'.split()
    # tokens1 = nltk.word_tokenize(s1)
    # tokens2 = nltk.word_tokenize(s2)
    # print(tokens1)
    # print(tokens2)
    print(sort_based_on_edit_distance(s1, [
        s2, s1, s3
    ]))


    a = [2,3,1,1,3,4,53,2,4]
    print(np.argsort(a))
