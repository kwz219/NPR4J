import codecs
import json
import os.path

import javalang

from CoCoNut.tokenization.tokenization import get_strings_numbers, token2statement
from Utils.IOHelper import readF2L, writeL2F
import numpy as np
"""
Recovery abstract code to a concrete form
"""
def post_edit(str):
    edit_list=["> =","< =","= =","! ="]
    for op in edit_list:
        str=str.replace(op)
    return str
def Recovery_Tufano(ids_f,map_dir,preds_f,nbest=10):
    ids=readF2L(ids_f)
    n_preds=readF2L(preds_f)
    assert  len(ids)==len(n_preds)

def Recovery_Tufano_one(ori_str,wordmap:dict):
    reverse_map=dict()
    for key in wordmap.keys():
        reverse_map[wordmap.get(key)]=key
    ranked_keys=sorted(list(reverse_map.keys()),key= lambda x: int(x.split('_')[1]),reverse=True)
    for key in ranked_keys:
        ori_str=ori_str.replace(key,reverse_map.get(key).strip())
    final_str=ori_str.replace('\n','').replace('\r','')
    return final_str
def Recovery_CoCoNut_one(buggy_file,pred_str):
    strings,numbers=get_strings_numbers_from_file(buggy_file)
    recovery_tokens=pred_str.split()
    recovery_str=token2statement(recovery_tokens,numbers,strings)
    #print(recovery_str)
    if len(recovery_str)==0:
        recovery_str=[pred_str]
    return recovery_str[0]

def get_strings_numbers_from_file(file_path):
    numbers_set = set()
    strings_set = set()
    with open(file_path, 'r') as file:
        data = file.readlines()
        for _, line in enumerate(data):
            strings, numbers = get_strings_numbers(line)
            numbers_set.update(numbers)
            strings_set.update(strings)
    return list(strings_set), list(numbers_set)

def Recovery_CoCoNut_all(preds_f,ids_f,buggy_lines_dir,buggy_methods_dir,buggy_classes_dir,output_dir,candi_size=100):
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    assert len(preds) % (candi_size + 2) == 0
    ind_list = list(range(0, len(preds), (candi_size+2)))
    for i in ind_list:
        group = preds[i:i+candi_size+2]
        idx= group[2].split('\t')[0]
        idx=int(idx[2:])
        id=ids[idx]
        id_buggyline=codecs.open(buggy_lines_dir+'/'+id+'.txt','r',encoding='utf8').read().strip()
        id_buggymethod=codecs.open(buggy_methods_dir+'/'+id+'.txt','r',encoding='utf8').read()
        patches_dict=dict()
        for pid,pred in enumerate(group[2:]):
            pred=pred.split('\t')[-1]
            rec_line=Recovery_CoCoNut_one(buggy_classes_dir+'/'+id+'.java',pred)
            rec_method=id_buggymethod.replace(id_buggyline,rec_line)
            patches_dict[str(pid)]=rec_method
        with open(output_dir+'/'+id+'.txt','w',encoding='utf8')as f:
            json.dump(patches_dict,f,indent=2)
            f.close()
        print(i)
    print('='*100)
def Recovery_Codit_all(results_f,files_f,buggy_lines_dir,buggy_methods_dir,output_f):
    lines=readF2L(results_f)
    files=readF2L(files_f)

    np_lines=np.array(lines)
    group_sep=lines[208]
    indices=np.where(np_lines==group_sep)[0]
    inds=indices.tolist()
    inds=[0]+inds
    print(inds)
    fix_dict=dict()

    def get_tokenized_str(code):
        tokens = list(javalang.tokenizer.tokenize(code))
        tokens = [t.value for t in tokens]
        return ' '.join(tokens)
    for i in range(len(inds)-1):
        group=lines[inds[i]:inds[i+1]]
        #print(len(group))
        if group[0]=='':
            id_index = int(group[1])
            label = group[4].strip()
            buggy_line = group[2].strip()
            fl_group = group[8:]
        else:
            id_index = int(group[0])
            label = group[3].strip()
            buggy_line = group[1].strip()
            fl_group = group[7:]
        patches_dict=dict()
        str_match=0
        if group[-1]=="True":
            str_match=1
        idx=0
        id = files[id_index].split('\\')[-1].replace('.txt', '')


        for fix_line in fl_group:
            if len(fix_line)>2 and (not fix_line=="True") and (not fix_line=="False"):

                buggy_method=codecs.open(buggy_methods_dir+'/'+id+".txt",'r',encoding='utf8').read().strip()
                #print(fix_line)
                buggy_method=get_tokenized_str(buggy_method)
                buggy_line=get_tokenized_str(buggy_line)
                fix_line=get_tokenized_str(fix_line)
                fix_method=buggy_method.replace(buggy_line,fix_line)
                if buggy_line not in buggy_method:
                    print("not in ")
                else:
                    print("in")
                patches_dict[str(idx)]=fix_method
                if fix_line.strip()==label:
                    str_match=idx
                    print('str_match',str_match)
                idx+=1
        fix_dict[id]={"match_result":str_match,"patches":patches_dict}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(fix_dict,f,indent=2)


def Recovery_Edits(benchmark_dir,patches_f,output_f):

    patches=json.load(codecs.open(patches_f,'r',encoding='utf8'))
    bears_ids=readF2L(benchmark_dir+'/bears.ids')
    qbs_ids=readF2L(benchmark_dir+'/qbs.ids')
    bdjar_ids=readF2L(benchmark_dir+'/bdjar.ids')
    d4j_ids=readF2L(benchmark_dir+'/d4j.ids')
    final_dict=dict()
    for id in patches.keys():
        content = patches.get(id)
        if id in bears_ids:
            id="bears_"+id
        if id in d4j_ids:
            id='d4j_'+id
        if id in qbs_ids:
            id='qbs_'+id
        if id in bdjar_ids:
            id='bdjar_'+id
        buggy_method_f=benchmark_dir+'/buggy_methods/'+id+'.txt'
        buggy_line_f=benchmark_dir+'/buggy_lines/'+id+'.txt'
        if os.path.exists(buggy_method_f) and os.path.exists(buggy_line_f):
            buggy_method=codecs.open(buggy_method_f,'r',encoding='utf8').read().strip()
            buggy_line=codecs.open(buggy_line_f,'r',encoding='utf8').read().strip()
            candidates=content["patches"]

            recover_candidates={}
            for cid in candidates.keys():
                candi=candidates.get(cid).replace('\t',' ')
                rec_method=buggy_method.replace(buggy_line," "+candi+" ")
                recover_candidates[cid]=rec_method
            final_dict[id]={"match_result":content["match_result"],"patches":recover_candidates}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)
#Recovery_Edits("F:/NPR_DATA0306/Evaluationdata/Benchmark",r"F:\NPR_DATA0306\FixResults\Final_Results\Edit_Benchmark.patches",r"F:\NPR_DATA0306\FixResults\Final_Results\Edits_Benchmark.txt")


"""
for identical check
recovery label
"""
def Recovery_Tufano_target(ids_f,target_dir,output_f):
    ids=readF2L(ids_f)
    recover_tgts=[]
    for id in ids:
        ori_str=codecs.open(target_dir+'/'+id+"_fix.txt.abs",'r',encoding='utf8').read()
        map=eval(codecs.open(target_dir+'/'+id+"_fix.txt.abs.map",'r',encoding='utf8').read())
        rec_str=Recovery_Tufano_one(ori_str,map)
        recover_tgts.append(Recovery_Tufano_one(rec_str,map))
    writeL2F(recover_tgts,output_f)
#Recovery_Tufano_target(r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\Tufano\benchmark.ids","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/tgtabs")
Recovery_Tufano_target("D:/RawData_Processed/Tufano/qbs_test.sids","D:/RawData_Processed/Tufano/temp/temp","D:/RawData_Processed/Tufano/qbs_test.fix.recovery")
"""
recovery Tufano's predictions, using map files generated during
the preprocessing phase
"""
def Recovery_Tufano_preds(ids_f,preds_f,candi_size,map_dir,output_f):
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    print(len(ids))
    print(len(preds))
    assert len(preds)/len(ids)==candi_size
    recover_preds=[]
    for i in range(len(ids)):
        map_f=map_dir+'/'+ids[i]+"_buggy.txt.abs.map"
        map=json.load(codecs.open(map_f,'r',encoding='utf8'))
        print(ids[i])

        per_preds=preds[i*candi_size:(i+1)*candi_size]
        for pred in per_preds:
            re_pred=Recovery_Tufano_one(pred,map)
            recover_preds.append(re_pred)
    assert len(recover_preds)==len(preds)
    writeL2F(recover_preds,output_f)
#Recovery_Tufano_preds("D:/RawData_Processed/Tufano/bdj_test.sids","/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_bdjar.pred",
                      #300,"D:/RawData_Processed/Tufano/temp/temp","/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_bdjar.pred.recovery")
#Recovery_Tufano_preds("D:/RawData_Processed/Tufano/bears_test.sids","D:/NPR4J-Pred/bears/Tufano/Tufano_b300_bears.pred",
                      #300,"D:/RawData_Processed/Tufano/temp/temp","D:/NPR4J-Pred/bears/Tufano/Tufano_b300_bears.pred.recovery")
#Recovery_Tufano_preds("D:/RawData_Processed/Tufano/d4j_test.sids","D:/NPR4J-Pred/d4j/Tufano/Tufano_b300_d4j.pred",
                      #300,"D:/RawData_Processed/Tufano/temp/temp","D:/NPR4J-Pred/d4j/Tufano/Tufano_b300_d4j.pred.recovery")
#Recovery_Tufano_preds("D:/RawData_Processed/Tufano/qbs_test.sids","D:/RawData_Processed/Tufano/qbs_test.fix",
                      #1,"D:/RawData_Processed/Tufano/temp/temp","D:/RawData_Processed/Tufano/qbs_test.fix.recovery")
Recovery_Tufano_preds("D:/RawData_Processed/Tufano/bears_test.sids","D:/RawData_Processed/Tufano/bears_test.fix",
                      1,"D:/RawData_Processed/Tufano/temp/temp","D:/RawData_Processed/Tufano/bears_test.fix.recovery")
#Recovery_Tufano_preds("D:/RawData_Processed/Tufano/d4j_test.sids","D:/RawData_Processed/Tufano/d4j_test.fix",
                      #1,"D:/RawData_Processed/Tufano/temp/temp","D:/RawData_Processed/Tufano/d4j_test.fix.recovery")



def Recovery_SequenceR_Method(fix_line,buggy_method_f,buggyline_id):
    buggy_method=codecs.open(buggy_method_f,'r',encoding='utf8').read().splitlines()
    buggy_line=buggy_method[buggyline_id]
    indent=buggy_line[:(len(buggy_line)-len(buggy_line.lstrip()))]
    buggy_method[buggyline_id]=indent+fix_line
    return buggy_method

def get_tokenized_str(code):
    tokens = list(javalang.tokenizer.tokenize(code))
    tokens = [t.value for t in tokens]
    return ' '.join(tokens)
def Recovery_SequenceR_Method2(fix_line,buggy_method_f,buggyline):
    buggy_method = codecs.open(buggy_method_f, 'r', encoding='utf8').read().splitlines()
    buggy_method = get_tokenized_str(buggy_method)
    buggy_line=get_tokenized_str(buggyline)
    fix_line=get_tokenized_str(fix_line)
    return buggy_method.replace(buggy_line,fix_line)


def Recovery_SequenceR_Method_All(candi_size,fix_file,ids_f,metas_dir,b_methods_dir,b_lines_dir,output_dir):
    ids=readF2L(ids_f)
    fix_lines=readF2L(fix_file)
    assert len(ids)*candi_size==len(fix_lines)
    for i in range(len(ids)):
        id=ids[i]
        fix_candidates=fix_lines[i*100:(i+1)*100]
        fix_dict={}

        prefix=["bdjar_","d4j_","qbs_","bears_"]
        for pf in prefix:
            meta_f=metas_dir+'/'+pf+id+'.txt'
            if os.path.exists(meta_f):
                break
        for pf in prefix:
            buggy_method_f=b_methods_dir+'/'+pf+id+'.txt'
            if os.path.exists(buggy_method_f):
                break
        metas=codecs.open(meta_f,'r',encoding='utf8').read().split('<sep>')
        buggyline_id=int(metas[2][1:].split(":")[0])
        for cid,cand in enumerate(fix_candidates):
            fix_method=Recovery_SequenceR_Method(cand,buggy_method_f,buggyline_id)
            fix_dict[str(cid)]=fix_method
        with open(output_dir+"/"+id+".fix",'w',encoding='utf8')as f:
            json.dump(fix_dict,f,indent=2)
        print(i)

def rewrite_ids(original_ids_f,d4j_ids_f,bears_ids_f,qbs_ids_f,bdjar_ids_f):
    original_ids=readF2L(original_ids_f)
    d4j_ids=readF2L(d4j_ids_f)
    bears_ids=readF2L(bears_ids_f)
    qbs_ids=readF2L(qbs_ids_f)
    bdjar_ids=readF2L(bdjar_ids_f)
    re_ids=[]
    for id in original_ids:
        if id in d4j_ids:
            re_ids.append('d4j_'+id)
        elif id in bears_ids:
            re_ids.append('bears_' + id)
        elif id in qbs_ids:
            re_ids.append('qbs_'+id)
        elif id in bdjar_ids:
            re_ids.append('bdjar_'+id)
    assert len(re_ids)==len(original_ids)
    writeL2F(re_ids,"F:/NPR_DATA0306/FixResults/SR_results/benchmark.ids")

#Recovery_SequenceR_Method_All(100,r"F:\NPR_DATA0306\Bears_pred\SequenceR\SR_26_bears.pred",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.sids",
           #                   "F:/NPR_DATA0306/Evaluationdata/Benchmark/metas","F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods","F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines",
             #                 "F:/NPR_DATA0306/Bears_pred/SequenceR")

#Recovery_Codit_all(r"F:\NPR_DATA0306\Bears_pred\full_report\details\bears_trans_100.2_200_codit_result.txt",r"F:\NPR_DATA0306\Processed_Codit_Bears\test\files.txt",
                  # "F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods","F:/NPR_DATA0306/FixResults/Final_Results/Codit_Bears.patches")
"""
Recovery_Tufano_all("F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Tufano/diversity_.ids","F:/NPR_DATA0306/FixResults/Tufano_3/Tufano_3_nb100_diversity.pred",
                    100,"F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/srcabs","F:/NPR_DATA0306/FixResults/Tufano_3/Tufano_3_nb100_diversity.recovery")

#Recovery_Tufano_all("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/Tufano_bears.ids","F:/NPR_DATA0306/Bears_pred/Tufano/Tufano_bears_b100.pred",
                    #100,"F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/srcabs","F:/NPR_DATA0306/Bears_pred/Tufano/Tufano_bears_b100.recovery")

Recovery_Tufano_target("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/Tufano_bears.ids","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/tgtabs")

Recovery_CoCoNut_all("F:/NPR_DATA0306/Bears_pred/CoCoNut_5_save/pred.txt","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
                     "F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines","F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods",
                     "F:/NPR_DATA0306/Bears_pred/CoCoNut_5_save",candi_size=100)
"""


