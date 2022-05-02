import codecs
import difflib
import json
import re



def readF2L(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
def calculate_min_samples(ids_f,buggy_lines_dir,buggy_lines_f,output_f):


    trn_buggylines=readF2L(buggy_lines_f)

    all_ids=readF2L(ids_f)


    def get_toked_line(buggy_line):

        first_round=re.split(r"([.,!?;(){}\s+])", buggy_line)
        final_tokens=[]
        for word in first_round:
            if word =='' or word.isspace():
                continue
            else:
                final_tokens.append(word)
        return ' '.join(final_tokens)

    sub_ids=all_ids[0:2000]
    def get_max_similarity(buggyline,trn_lines):
        similar=0
        for trn_line in trn_lines:
            toked_buggy = get_toked_line(buggyline.strip())
            toked_trn = get_toked_line(trn_line.strip())
            status = difflib.SequenceMatcher(None, toked_buggy, toked_trn)
            similarity=status.ratio()
            similar=max(similar,similarity)
            if similar==1:
                return 1
        return  similar
    for idx, id in enumerate(sub_ids):
        if True:
            buggy_line = codecs.open(buggy_lines_dir + '/' + id + '.txt', 'r', encoding='utf8').read().strip()

            simialr=get_max_similarity(buggy_line,trn_buggylines)
            with open(output_f,'a',encoding='utf8')as f :
                f.write(id+' '+str(simialr)+'\n')

            print(idx,id,str(simialr))
calculate_min_samples("/root/zwk/Analyze/final.ids","/root/zwk/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","/root/zwk/NPR_DATA0306/train_lines/train_lines.buggy","/root/zwk/Analyze/all.ids1")