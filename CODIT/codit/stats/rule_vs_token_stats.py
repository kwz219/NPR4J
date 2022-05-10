if __name__ == '__main__':
    token_file = '../../correct_ids/codit.original.abstract.token.only_10.txt'
    rule_file = '../../correct_ids/codit.original.abstract.rule.only_10.txt'
    tf = open(token_file)
    rf = open(rule_file)
    correct_tokens = set()
    correct_rules = set()
    for l in tf:
        correct_tokens.add(int(l.strip()))
    for l in rf:
        correct_rules.add(int(l.strip()))
    common = sorted(correct_rules.intersection(correct_tokens))
    only_tokens = sorted(correct_tokens.difference(correct_rules))
    only_rules = sorted(correct_rules.difference(correct_tokens))
    total = sorted(correct_tokens.union(correct_rules))
    print(common)
    print(only_tokens)
    print(only_rules)
    print(total)
    print(len(common))
    print(len(only_tokens))
    print(len(only_rules))
    print(len(total))
