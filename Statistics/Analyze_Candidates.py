import codecs
import difflib
import json
import re

import numpy as np
import pandas as pd

from Utils.IOHelper import readF2L


def get_candidates_num_analyze(diversity_f):
    diversity_result=codecs.open(diversity_f,'r',encoding='utf8')

    d_re=json.load(diversity_result)

    re_list=np.array(list(d_re.values()))
    series=pd.Series(re_list)
    check_range=list(range(0,100,5))
    statistics_dict=dict()
    statistics_dict["1"]=sum(re_list==0)
    for start in check_range:
        count=sum(series.between(0,start+4)==True)
        statistics_dict[str(start+5)]=count
    return statistics_dict
#s_dict=get_candidates_num_analyze(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval")
#for key in s_dict.keys():
    #print(str(round(int(s_dict[key])/12815 *100,2))+'%')
def count_unique_bugs(CoCoNuts_paths,Recoder_paths,Edits_paths,CODIT_paths,SequenceR_paths,Tufano_paths):
    def get_hitids(paths):
        id_set=set()
        for path in paths:
            patches=json.load(codecs.open(path,'r',encoding='utf8'))
            for key in patches.keys():
                if int(patches.get(key))>-1:
                    if "bdjar_" in key:
                        key=key.replace("bdjar_","")
                    id_set.add(key)
        return id_set
    Hit_CoCoNut=get_hitids(CoCoNuts_paths)
    Hit_Recoder=get_hitids(Recoder_paths)
    Hit_Edits=get_hitids(Edits_paths)
    Hit_CODIT=get_hitids(CODIT_paths)
    Hit_SR=get_hitids(SequenceR_paths)
    Hit_Tufano=get_hitids(Tufano_paths)
    Unique_CoCoNut=Hit_CoCoNut-(Hit_Recoder|Hit_Edits|Hit_CODIT|Hit_SR|Hit_Tufano)
    Unique_Recoder=Hit_Recoder-(Hit_CoCoNut|Hit_Edits|Hit_CODIT|Hit_SR|Hit_Tufano)
    Unique_Edits = Hit_Edits - (Hit_CoCoNut | Hit_Recoder | Hit_CODIT | Hit_SR | Hit_Tufano)
    Unique_CODIT = Hit_CODIT - (Hit_CoCoNut | Hit_Edits | Hit_Recoder | Hit_SR | Hit_Tufano)
    Unique_SR = Hit_SR - (Hit_CoCoNut | Hit_Edits | Hit_CODIT | Hit_Recoder | Hit_Tufano)
    Unique_Tufano = Hit_Tufano - (Hit_CoCoNut | Hit_Edits | Hit_CODIT | Hit_SR | Hit_Recoder)
    print("CoCoNut",len(Hit_CoCoNut),len(Unique_CoCoNut))
    print("Recoder",len(Hit_Recoder),len(Unique_Recoder))
    print("Edits",len(Hit_Edits),len(Unique_Edits))
    print("CODIT",len(Hit_CODIT),len(Unique_CODIT))
    print("SR",len(Hit_SR),len(Unique_SR))
    print("Tufano",len(Hit_Tufano),len(Unique_Tufano))

    print("all_fix",len(Hit_Recoder|Hit_Edits|Hit_CODIT|Hit_SR|Hit_Tufano|Hit_CoCoNut))

#count_unique_bugs([r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_bdjar.final.eval"],
 #                 [r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_new_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_bdjar.final.eval"],
  #                [r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\Edits_bdjar.final.eval"],
   #               [r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\Codit_bdjar.final.eval"],
    #              [r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_bdjar.final.eval"],
      #            [r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_diversity.eval",r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_bdjar.final.eval"])

def analyze_generalizability(eval_result,buggy_lines_dir,trn_data_f):
    eval_result=json.load(codecs.open(eval_result,'r',encoding='utf8'))
    hit_total=0
    in_trn=0
    nin_trn=0
    trn_data=codecs.open(trn_data_f).read()
    for idx,id in enumerate(eval_result.keys()):
        hit_result=int(eval_result[id])
        if hit_result>0:
            hit_total+=1
            buggy_line=codecs.open(buggy_lines_dir+'/'+id+'.txt','r',encoding='utf8').read().strip()
            if buggy_line in trn_data:
                in_trn+=1
            else:
                nin_trn+=1
        print(idx,hit_total,in_trn)
    print("hit_total",hit_total)
    print("in_total",in_trn)
    print("nin_trn",nin_trn)
#analyze_generalizability(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines",r"F:\NPR_DATA0306\Processed_SR\trn.buggy")
def getDiffType(buggy_line,fix_line):
    def get_toked_line(buggy_line):

        first_round=re.split(r"([.,!?;(){}\s+])", buggy_line)
        final_tokens=[]
        for word in first_round:
            if word =='' or word.isspace():
                continue
            else:
                final_tokens.append(word)
        return ' '.join(final_tokens)

    toked_buggy=get_toked_line(buggy_line.strip())
    toked_fix=get_toked_line(fix_line.strip())
    status = difflib.SequenceMatcher(None, toked_buggy, toked_fix)
    tagset=[]
    for tag, i1, i2, j1, j2 in status.get_opcodes():
        #print("%7s a[%d:%d] (%s) b[%d:%d] (%s)" % (tag, i1, i2, toked_buggy[i1:i2], j1, j2,toked_fix[j1:j2]))
        if tag == "equal":
            continue
        tagset.append(tag)
    tagset=list(set(tagset))
    if len(tagset)==1:
        if tagset[0]=="replace":
            return "simple_replace"
        elif tagset[0]=="delete":
            return "simple_delete"
        elif tagset[0]=="insert":
            return "simple_insert"
        else:
            return "unknown"
    else:
        return "mixed"

def analyze_fixed_type(eval_result_f,buggy_lines_dir,fix_lines_dir):
    eval_result=json.load(codecs.open(eval_result_f,'r',encoding='utf8'))
    hit_total=0
    all_count={"simple_replace":2078,"simple_delete":1718,"simple_insert":4532,"mixed":4487}
    diff_count={"simple_replace":0,"simple_delete":0,"simple_insert":0,"mixed":0}
    diff_ids={"simple_replace":[],"simple_delete":[],"simple_insert":[],"mixed":[]}
    for idx,id in enumerate(eval_result.keys()):
        buggy_line = codecs.open(buggy_lines_dir + '/' + id + '.txt', 'r', encoding='utf8').read().strip()
        fix_line = codecs.open(fix_lines_dir + '/' + id + '.txt', 'r', encoding='utf8').read().strip()
        difftype = getDiffType(buggy_line, fix_line)
        ori_count = all_count[difftype]
        #all_count.update({difftype: ori_count + 1})
        hit_result = int(eval_result[id])
        if hit_result > -1:
            hit_total += 1

            ori_count=diff_count[difftype]
            diff_count.update({difftype:ori_count+1})

            ori_list=diff_ids[difftype]
            ori_list.append(id)
            diff_ids.update({difftype:ori_list})
            #print(diff_count)
    print(eval_result_f)
    #print(all_count)
    result_dict={}
    for key in diff_count.keys():
        result_dict[key]=str(round(diff_count[key]/all_count[key]*100,2))+'%'
    print(result_dict)
    print('=' * 100)
    return diff_ids
def caculate_min_samples(eval_f,buggy_lines_dir,buggy_lines_f,output_f):
    distances_dict={}
    eval_result = json.load(codecs.open(eval_f, 'r', encoding='utf8'))
    trn_buggylines=readF2L(buggy_lines_f)
    res=readF2L(output_f)
    dis_f=codecs.open(output_f,'a',encoding='utf8')
    idset=set()
    for id in res:
        idset.add(id.split()[0])

    def get_toked_line(buggy_line):

        first_round=re.split(r"([.,!?;(){}\s+])", buggy_line)
        final_tokens=[]
        for word in first_round:
            if word =='' or word.isspace():
                continue
            else:
                final_tokens.append(word)
        return ' '.join(final_tokens)


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
    in_count=0
    total_count=0
    for idx, id in enumerate(eval_result.keys()):
        hit_result = int(eval_result[id])
        if hit_result > -1:
            if id in idset:
                print("exists")
                continue
            buggy_line = codecs.open(buggy_lines_dir + '/' + id + '.txt', 'r', encoding='utf8').read().strip()

            simialr=get_max_similarity(buggy_line,trn_buggylines)
            dis_f.write(id+' '+str(simialr)+'\n')
            print(idx)



#caculate_min_samples(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines",r"F:\NPR_DATA0306\train\train_lines.buggy",r"F:\NPR_DATA0306\Analyze\distance\all.dis")

#SequenceR_diffids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")
#Recoder_diff_ids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_new_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")
#CoCoNut_diff_ids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")
#Codit_diff_ids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")
#Edits_diff_ids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")
#Tufano_diff_ids=analyze_fixed_type(r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_diversity.eval","F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines")

"""
all_count={"simple_replace":2078,"simple_delete":1718,"simple_insert":4532,"mixed":4487}
all_hit={"simple_replace":set(),"simple_delete":set(),"simple_insert":set(),"mixed":set()}
all_ids=[SequenceR_diffids,Recoder_diff_ids,CoCoNut_diff_ids,Codit_diff_ids,Edits_diff_ids,Tufano_diff_ids]
for id in all_ids:
    for type in id.keys():
        hit_ids=id[type]
        ori_set=all_hit[type]
        for item in hit_ids:
            ori_set.add(item)
for key in all_hit.keys():
    print(key,len(all_hit[key]))
    """