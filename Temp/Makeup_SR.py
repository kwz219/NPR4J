import codecs
import re


def makeup_SequenceR(input_dir,ids_f,buggy_f,fixes_f,output_f,vocab_lines_f):
    ids=[]
    with open(ids_f,'r',encoding='utf8')as f:
        for line in f:
            ids.append(line.strip())
        f.close()
    fixes=[]
    with open(fixes_f,'r',encoding='utf8')as f:
        for line in f:
            fixes.append(line.strip())
        f.close()
    assert len(ids)==len(fixes)
    buggy_lines=[]
    with open(buggy_f,'r',encoding='utf8')as f:
        for line in f:
            buggy_lines.append(line.strip())
        f.close()

    vocab_lines=[]
    new_fixes=[]
    for id,fix in zip(ids,fixes):
        if fix.isspace() or len(fix)<=1:
            fix_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt').read()
            if fix_line.isspace() or len(fix)==0:
                new_fixes.append("<DELETE>")
            else:
                toked_fix = re.split(r"([.,!?;(){}])", fix_line)
                toked_fix = ' '.join(toked_fix)
                new_fixes.append(toked_fix)
        else:
            new_fixes.append(fix)
    for b_line in buggy_lines:
        b_line=b_line
        bs_ind=b_line.index("<START_BUG>")
        be_ind=b_line.index("<END_BUG>")


        vocab_lines.append(b_line[int(bs_ind//1.2):int((len(buggy_lines)-be_ind)//5)+be_ind])

    assert len(ids)==len(new_fixes)==len(vocab_lines)

    filter_ids=[]
    filter_fixes=[]
    filter_buggy=[]

    with open(output_f,'w',encoding='utf8')as f:
        for line in new_fixes:
            f.write(line+'\n')
        f.close()
    with open(vocab_lines_f,'w',encoding='utf8')as vf:
        for line in vocab_lines:
            vf.write(line+'\n')
makeup_SequenceR("/home/zhongwenkang3/NPR4J_Data/BigTrain","/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_trn.sids",
"/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_trn.buggy",
                 "/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_trn.fix.ori",
                 "/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_trn.fix",
                 "/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_v.buggy")
