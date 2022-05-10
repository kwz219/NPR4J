from tqdm import tqdm


def remove_junk(str):
    new_str = []
    for char in str:
        if not ord(char) <= 32:
            new_str.append(char)
    return ''.join(new_str)


if __name__ == '__main__':
    with open('../my_data/data.txt', encoding='utf-8') as fp:
        data = fp.readlines()

    for i, line in enumerate(tqdm(data)):
        line = line.split('###')
        buggy = line[1]
        pos = line[2]
        fix = line[3]

        buggy = remove_junk(buggy)
        fix = remove_junk(fix)

        buggy = buggy.split()
        pos = pos.split()
        fix = fix.split()


        line[1] = '\t'.join(buggy)
        line[2] = '\t'.join(pos)
        line[3] = '\t'.join(fix)

        while ' ' in line[1]:
            line[1] = line[1].replace(' ', '')

        while ' ' in line[3]:
            line[3] = line[3].replace(' ', '')

        data[i] = '###'.join(line)


    with open('my_data/data.txt', 'w', encoding='utf-8') as fp:
        for line in tqdm(data):
            fp.write(line)
            fp.write('\n')

    with open('my_data/data.txt', encoding='utf-8') as fp:
        data = fp.readlines()
    print(len(data))
    count = 0
    for line in tqdm(data):
        for c in line:
            num = ord(c)
            if num <= 31:
                if not (num == 9 or num == 10):
                    count += 1


    print(count)

