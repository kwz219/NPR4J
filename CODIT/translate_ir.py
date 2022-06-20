import numpy as np

import CODIT.util


def read_examples(_src, _tgt):
    examples = []
    with open(_src) as s:
        with open(_tgt) as t:
            for i, (il, ol) in enumerate(zip(s, t)):
                il = [token.strip() for token in il.strip().split()]
                ol = [token.strip() for token in ol.strip().split()]
                examples.append((il, ol))
            return examples
    pass


def calc_score(tri, ti):
    tr_words = set(tri)
    t_words = set(ti)
    common = len(tr_words.intersection(t_words))
    all_words = len(tr_words.union(t_words))
    return float(common) / float(all_words)
    pass


def calculate_sim(train_examples, ti, to, max_samples=10):
    train_examples = np.array(train_examples)
    scores = []
    for (tri, _) in train_examples:
        scores.append(calc_score(tri, ti))
    indices = np.argsort(scores)[::-1][:max_samples]
    predictions = train_examples[indices]
    pred_scores = []
    for p in predictions:
        pred_scores.append(calc_score(p[1], to))
    return pred_scores
    pass


def get_edit_sim(org_code, cand_code):
    if isinstance(org_code, str):
        org_parts = [part.strip() for part in org_code.split()]
        cand_parts = [part.strip() for part in cand_code.split()]
    else:
        org_parts = org_code
        cand_parts = cand_code
    def levenshteinDistance(s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    return 0 - levenshteinDistance(org_parts, cand_parts)
    pass


def find_similar_matches(train_examples, test_examples):
    train_examples = np.array(train_examples)
    test_examples = np.array(test_examples)
    total_correct_1 = 0
    total_correct_2 = 0
    total_correct_5 = 0
    total_correct_10 = 0
    for i in range(len(test_examples)):

        ti, to = test_examples[i]
        similarity_scores = calculate_sim(train_examples, ti, to)
        if i % 100 == 0:
            util.debug(i, total_correct_10)
            # util.debug(similarity_scores)
        # print(similarity_scores)
        if similarity_scores[0] > 0.999:
            total_correct_1 += 1
        if np.max(similarity_scores[:2]) > 0.999:
            total_correct_2 += 1
        if np.max(similarity_scores[:5]) > 0.999:
            total_correct_5 += 1
        if np.max(similarity_scores) > 0.999:
            total_correct_10 += 1
    return total_correct_1, total_correct_2, total_correct_5, total_correct_10
    pass


if __name__ == '__main__':
    ir_output_file = open('full_report/ir_result.tsv', 'a')
    for data_source in ['10-20', 'code_change_data']:
        train_src = '/home/saikatc/Research/OpenNMT-py/data/raw/' + data_source + '/train/prev.token'
        train_tgt = '/home/saikatc/Research/OpenNMT-py/data/raw/' + data_source + '/train/next.token'
        test_src = '/home/saikatc/Research/OpenNMT-py/data/raw/' + data_source + '/test/prev.token'
        test_tgt = '/home/saikatc/Research/OpenNMT-py/data/raw/' + data_source + '/test/next.token'

        train_examples = read_examples(train_src, train_tgt)
        test_examples = read_examples(test_src, test_tgt)
        exact_match = [data_source]
        exact_match.extend([str(r) for r in list(find_similar_matches(train_examples, test_examples))])
        result = '\t'.join(exact_match)
        ir_output_file.write(result + '\n')
    ir_output_file.close()


