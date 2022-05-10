import sys, os


if __name__ == '__main__':
    dataset = '/home/saikatc/Research/OpenNMT-py/c_data/filtered/abstract/test'#sys.argv[0]
    prev_token_file = os.path.join(dataset, 'prev.token')
    next_token_file = os.path.join(dataset, 'next.token')
    p_file = open(prev_token_file)
    n_file = open(next_token_file)
    count = 0
    for i, (p_line, n_line) in enumerate(zip(p_file, n_file)):
        assert isinstance(p_line, str) and isinstance(n_line, str)
        p_line = p_line.strip()
        n_line = n_line.strip()
        p_parts = p_line.split()
        n_parts = n_line.split()
        p_vars = set()
        n_vars = set()
        for pw in p_parts:
            pw = pw.strip()
            if '_' in pw:
                p_vars.add(pw)
        found =  False
        for nw in n_parts:
            nw = nw.strip()
            if '_' in nw:
                # print(nw)
                if nw not in p_vars:
                    count += 1
                    print(i)
                    break
    print(count)
