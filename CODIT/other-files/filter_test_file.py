import os, sys
parent_file_path = 'data/10_20_abs.test.parent.code'
child_file_path = 'data/10_20_abs.test.child.code'

all_examples = []
total = 0
accounted = 0
parent_file = open(parent_file_path)
child_file = open(child_file_path)

for p, c in zip(parent_file, child_file):
    if p.strip() != c.strip():
        all_examples.append([p.strip(), c.strip()])
        accounted += 1
    total += 1
parent_file.close()
child_file.close()
print 'Total', total, 'Accepted' , accounted
os.remove(parent_file_path)
os.remove(child_file_path)

parent_file = open(parent_file_path, 'w')
child_file = open(child_file_path, 'w')

for ex in all_examples:
    parent_file.write(ex[0] + '\n')
    child_file.write(ex[1] + '\n')
parent_file.close()
child_file.close()