import re

from CoCoNut.tokenization.tokenization import extract_strings, COMPOSED_SYMBOLS, camel_case_split, number_split, \
    remove_integer


def CoCoNut_tokenize(string):
    final_token_list = []
    string_replaced = extract_strings(string)
    split_tokens = re.split(r'([\W_])', string_replaced)
    split_tokens = list(filter(lambda a: a not in [' ', '', '"', "'", '\t', '\n'], split_tokens))
    flag = False

    # Special symbols
    for idx, token in enumerate(split_tokens):
        if idx < len(split_tokens) - 1:
            reconstructed_token = token + split_tokens[idx + 1]
            if reconstructed_token in COMPOSED_SYMBOLS:
                final_token_list.append(reconstructed_token)
                flag = True
            elif not flag:
                final_token_list.append(token)
            elif flag:
                flag = False
        else:
            final_token_list.append(token)
    # Camel Case
    no_camel = []
    for token in final_token_list:
        camel_tokens = camel_case_split(token)
        for idx, camel_tok in enumerate(camel_tokens):
            no_camel.append(camel_tok)

    # number split
    tokens = []
    for token in no_camel:
        number_sep = number_split(token)
        for num in number_sep:
            tokens.append(num)
    tokens = remove_integer(tokens)
    for idx, token in enumerate(tokens):
        if token == 'SSSTRINGSS':
            if idx > 0 and tokens[idx - 1] == '$STRING$':
                return []
            else:
                tokens[idx] = '$STRING$'

    return tokens

