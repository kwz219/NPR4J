import codecs
import json
import os
import re
import numpy as np
import javalang
from Utils.IOHelper import readF2L
import pandas as pd
import csv
def hits_normal(candis:list,label:str):
    for idx,cand in enumerate(candis):
        if cand.strip()==label.strip():
            return idx
    return -1
def hits_ignorespace(candis:dict,label:str):
    pattern = re.compile(r'\s+');
    label_new=re.sub(pattern,'',label)
    idx=0
    for key in candis.keys():
        cand_new=re.sub(pattern,'',candis.get(key))
        #if label_new in cand_new or label_new==cand_new:
        if label_new == cand_new:
            return idx
        idx+=1
    return -1
def Evaluate_Edits(patches_f,fix_line_dir,output_f):
    patches=json.load(codecs.open(patches_f,'r',encoding='utf8'))
    Eval_dict={}
    ind=0

    for id in patches.keys():
        print(id)
        path=fix_line_dir+'/'+id+'.txt'
        d4j_path=fix_line_dir+'/d4j_'+id+'.txt'
        bdjar_path = fix_line_dir + '/bdjar_' + id + '.txt'
        qbs_path = fix_line_dir + '/qbs_' + id + '.txt'
        if os.path.exists(d4j_path):
            path=d4j_path
        elif os.path.exists(bdjar_path):
            path=bdjar_path
        elif os.path.exists(qbs_path):
            path=qbs_path
        if os.path.exists(path):
            fix_line=codecs.open(path,'r',encoding='utf8').read().strip()
            #print(fix_line)
            id_patches=patches.get(id)["patches"]
            eval_result=hits_ignorespace(id_patches,fix_line)
            Eval_dict[id]=eval_result
            print(ind)
            ind+=1
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(Eval_dict,f,indent=2)
        f.close()

def Evaluate_Edits_bears(patches_f,true_ids,fix_line_dir,output_f):
    patches = json.load(codecs.open(patches_f, 'r', encoding='utf8'))
    ids=readF2L(true_ids)
    Eval_dict={}
    ind=0
    for key in patches.keys():
        id=ids[int(key)]
        if True:
            path = fix_line_dir + '/' + "bears_"+id + '.txt'
            if os.path.exists(path):
                fix_line = codecs.open(path, 'r', encoding='utf8').read().strip()
                # print(fix_line)
                id_patches = patches.get(key)["patches"]
                eval_result = hits_ignorespace(id_patches, fix_line)
                Eval_dict[id] = eval_result
                print(ind)
                ind += 1
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(Eval_dict, f, indent=2)
        f.close()
Evaluate_Edits_bears(r"F:\NPR_DATA0306\FixResults\Final_Results\Bears.patches",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.sids",
                     "F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines","F:/NPR_DATA0306/Eval_result/benchmark_eval/Edits_bears.eval")
def transform_bdjar_eval(dir,prefixs,bdjar_f):
    def all_hit(re_dict,ids):
        result=1
        for id in ids:
            if id not in re_dict.keys():
                id="bdjar_"+id
            if id not in re_dict.keys():
                return -1
            if re_dict[id]==-1:
                return -1
        return result
    bdjar_infos=json.load(codecs.open(bdjar_f,'r',encoding='utf8'))
    for prefix in prefixs:
        path=dir+'/'+prefix+"_bdjar.eval"
        eval_ori=json.load(codecs.open(path,'r',encoding='utf8'))
        eval_final={}
        for bug in bdjar_infos.keys():
            ids=list(bdjar_infos.get(bug).keys())
            print(ids)
            eval_result=all_hit(eval_ori,ids)
            eval_final[bug]=eval_result
        with open(dir+'/'+prefix+'_bdjar.pure.eval','w',encoding='utf8')as f:
            json.dump(eval_final,f,indent=2)
            f.close()
transform_bdjar_eval("F:/NPR_DATA0306/Eval_result/diversity",["CoCoNut_union","Codit","SequenceR","Tufano","Edits","Recoder"],r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bdjar.json.pure")
exit(0)
def preprare_bearss_4check(benchs_f,output_dir,buggy_lines_dir,fix_lines_dir):
    benchmark=json.load(codecs.open(benchs_f,'r',encoding='utf8'))
    def load_eval_results(eval_f):
        eval_results=readF2L(eval_f)
        eval_dict={}
        for line in eval_results:
            infos=line.split()
            if infos[-1]=="passHumanTest":
                eval_dict[infos[0]]=infos[1]
        return eval_dict
    SR_eval=load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\SequenceR\SequenceR_eval.result")
    Edits_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\Edits\Edits_eval.result")
    Codit_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\Codit\Codit_eval.result")
    Tufano_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\Tufano\Tufano_eval.result")
    Recoder_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\Recoder\Recoder_eval.result")
    CoCoNut5_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut5\CoCoNut5_eval.result")
    CoCoNut12_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut12\CoCoNut12_eval.result")
    CoCoNut21_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut21\CoCoNut21_eval.result")
    CoCoNut33_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut33\CoCoNut33_eval.result")
    CoCoNut35_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut35\CoCoNut35_eval.result")
    CoCoNut99_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNut99\CoCoNut99_eval.result")
    CoCoNutC7_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNutC7\CoCoNutc7_eval.result")
    CoCoNutC9_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\bears\CoCoNutC9\CoCoNut_c9_eval.result")

    SR_bears=json.load(codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\SequenceR_Bears.patches",'r',encoding='utf8'))
    Edits_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Edits_bears.patches", 'r', encoding='utf8'))
    Codit_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Codit_Bears.patches", 'r', encoding='utf8'))
    Tufano_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Tufano_Bears.patches", 'r', encoding='utf8'))
    Recoder_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Recoder_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_5_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_5_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_12_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_12_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_21_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_21_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_33_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_33_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_35_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_35_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_99_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_99_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_c7_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_c7_Bears.patches", 'r', encoding='utf8'))
    CoCoNut_c9_bears = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_c9_Bears.patches", 'r', encoding='utf8'))

    all_dict={"SR":SR_eval,"Edits":Edits_eval,"Codit":Codit_eval,"Tufano":Tufano_eval,"Recoder":Recoder_eval,"CoCoNut5":CoCoNut5_eval,"CoCoNut12":CoCoNut12_eval,
              "CoCoNut21":CoCoNut21_eval,"CoCoNut33":CoCoNut33_eval,"CoCoNut35":CoCoNut35_eval,"CoCoNut99":CoCoNut99_eval,"CoCoNutC7":CoCoNutC7_eval,"CoCoNutC9":CoCoNutC9_eval}
    candidates_dict={"SR":SR_bears,"Edits":Edits_bears,"Codit":Codit_bears,"Tufano":Tufano_bears,"Recoder":Recoder_bears,"CoCoNut5":CoCoNut_5_bears,"CoCoNut12":CoCoNut_12_bears,
              "CoCoNut21":CoCoNut_21_bears,"CoCoNut33":CoCoNut_33_bears,"CoCoNut35":CoCoNut_35_bears,"CoCoNut99":CoCoNut_99_bears,"CoCoNutC7":CoCoNut_c7_bears,"CoCoNutC9":CoCoNut_c9_bears}
    multi_count=0
    for bugID in benchmark.keys():
        bug_infos=benchmark.get(bugID)
        if len(bug_infos.keys())==1:
            bears_id=list(bug_infos.keys())[0]
            buggy_line=codecs.open(buggy_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
            fix_line=codecs.open(fix_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
            buggy_method=bug_infos[bears_id]["buggy_method"].replace('\t',' ').split('\n')
            fix_method=bug_infos[bears_id]["fix_method"].replace('\t',' ').split('\n')
            check_dict={"BugID":bugID,"buggy_method":buggy_method,"fix_method":fix_method,"buggy_line":buggy_line,"fix_line":fix_line}

            plausible_dict={}
            for eval_name in all_dict.keys():
                bug_eval_re=all_dict.get(eval_name)
                bug_patches=candidates_dict[eval_name]
                if bugID in bug_eval_re.keys():
                    ind=bug_eval_re[bugID]
                    candidate=bug_patches[bears_id]["patches"][str(ind)]
                    plausible_dict[eval_name]={"manual_check":"None","reason":"None","pred":candidate.replace('\t',' ').split('\n')}
            if len(plausible_dict)>0:
                check_dict["plausible_patches"]=plausible_dict
                with open(output_dir+'/'+bugID+".check",'w',encoding='utf8')as df:
                    json.dump(check_dict,df,indent=2)
                print(bugID,"finished")
        else:
            ids=list(bug_infos.keys())
            check_dict = {"BugID": bugID}
            hit_count=0
            for idx,bears_id in enumerate(ids):
                buggy_line=codecs.open(buggy_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                fix_line=codecs.open(fix_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                buggy_method = bug_infos[bears_id]["buggy_method"].split('\n')
                fix_method = bug_infos[bears_id]["fix_method"].split('\n')
                check_dict["buggy_method"+'_'+str(idx)]=buggy_method
                check_dict["fix_method"+'_'+str(idx)]=fix_method
                check_dict["buggy_line" + '_' + str(idx)] = buggy_line
                check_dict["fix_line" + '_' + str(idx)] = fix_line
                plausible_dict = {}
                for eval_name in all_dict.keys():
                    bug_eval_re = all_dict.get(eval_name)
                    bug_patches = candidates_dict[eval_name]
                    if bugID in bug_eval_re.keys():
                        hit_count+=1
                        ind = bug_eval_re[bugID]
                        print(eval_name,bears_id,str(ind))
                        try:
                            candidate = bug_patches[bears_id]["patches"][str(ind)]
                        except:
                            continue
                        if eval_name in plausible_dict.keys():
                            plausible_dict[eval_name+"_"+str(idx)]["pred"] = candidate
                        else:
                            plausible_dict[eval_name+"_"+str(idx)]={"manual_check":"None","reason":"None","pred":candidate.replace('\t',' ').split('\n')}
                if len(plausible_dict.keys()) > 0:
                    check_dict["plausible_patches_"+str(idx)] = plausible_dict
            if hit_count>1:
                with open(output_dir+'/'+bugID+".check",'w',encoding='utf8')as df:
                     json.dump(check_dict,df,indent=2)
                     print(bugID,"finished")

#preprare_bearss_4check(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bears.json","F:/NPR_DATA0306/Eval_result/bears/Check",
                       #uggy_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines",
                       #fix_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines")

def preprare_quixbugs_4check(benchs_f,output_dir,buggy_lines_dir,fix_lines_dir):
    quixbugs=json.load(codecs.open(benchs_f,'r',encoding='utf8'))
    def load_eval_results(eval_f):
        eval_results=readF2L(eval_f)
        eval_dict={}
        for line in eval_results:
            infos=line.split()
            if infos[-1]=="passHumanTest":
                eval_dict[infos[0]]=infos[2]
        return eval_dict
    SR_eval=load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\SequenceR_eval.result")
    Edits_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\Edits_eval.result")
    Codit_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\Codit_eval.result")
    Tufano_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\Tufano_eval.result")
    Recoder_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\Recoder_eval.result")
    CoCoNut5_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut5_eval.result")
    CoCoNut12_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut12_eval.result")
    CoCoNut15_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut15_eval.result")
    CoCoNut32_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut32_eval.result")
    CoCoNut21_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut21_eval.result")
    CoCoNut33_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut33_eval.result")
    CoCoNut35_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut35_eval.result")
    CoCoNut99_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNut99_eval.result")
    CoCoNutC7_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNutc7_eval.result")
    CoCoNutC9_eval = load_eval_results(r"F:\NPR_DATA0306\Eval_result\qbs\CoCoNutc9_eval.result")

    SR_b=json.load(codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\SequenceR_Benchmark.patches",'r',encoding='utf8'))
    Edits_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Edits_Benchmark.txt", 'r', encoding='utf8'))
    Codit_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Codit_Benchmark.patches", 'r', encoding='utf8'))
    Tufano_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Tufano_Benchmark.patches", 'r', encoding='utf8'))
    Recoder_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\Recoder_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_5_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_5_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_12_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_12_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_15_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_15_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_21_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_21_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_32_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_32_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_33_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_33_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_35_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_35_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_99_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_99_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_c7_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_c7_Benchmark.patches", 'r', encoding='utf8'))
    CoCoNut_c9_b = json.load(
        codecs.open(r"F:\NPR_DATA0306\FixResults\Final_Results\CoCoNut_c9_Benchmark.patches", 'r', encoding='utf8'))

    all_dict = {"SR": SR_eval, "Edits": Edits_eval, "Codit": Codit_eval, "Tufano": Tufano_eval, "Recoder": Recoder_eval,
                "CoCoNut5": CoCoNut5_eval, "CoCoNut12": CoCoNut12_eval,
                "CoCoNut21": CoCoNut21_eval, "CoCoNut33": CoCoNut33_eval, "CoCoNut35": CoCoNut35_eval, "CoCoNut15":CoCoNut15_eval, "CoCoNut32":CoCoNut32_eval,
                "CoCoNut99": CoCoNut99_eval, "CoCoNutC7": CoCoNutC7_eval, "CoCoNutC9": CoCoNutC9_eval}
    candidate_dict = {"SR": SR_b, "Edits": Edits_b, "Codit": Codit_b, "Tufano": Tufano_b, "Recoder": Recoder_b,
                "CoCoNut5": CoCoNut_5_b, "CoCoNut12": CoCoNut_12_b,
                "CoCoNut21": CoCoNut_21_b, "CoCoNut33": CoCoNut_33_b, "CoCoNut35": CoCoNut_35_b, "CoCoNut15":CoCoNut_15_b, "CoCoNut32":CoCoNut_32_b,
                "CoCoNut99": CoCoNut_99_b, "CoCoNutC7": CoCoNut_c7_b, "CoCoNutC9": CoCoNut_c9_b}
    for bugID in quixbugs.keys():
        bug_infos=quixbugs.get(bugID)
        bugname=bug_infos["name"]
        buggy_method = bug_infos["buggy_method"].replace('\t', ' ').split('\n')
        fix_method = bug_infos["fix_method"].replace('\t', ' ').split('\n')
        buggy_line=codecs.open(buggy_lines_dir+'/'+bugID+'.txt','r',encoding='utf8').read().strip()
        fix_line=codecs.open(fix_lines_dir+'/'+bugID+'.txt','r',encoding='utf8').read().strip()
        check_dict = {"BugName": bugname, "buggy_method": buggy_method, "fix_method": fix_method,"buggy_line":buggy_line,"fix_line":fix_line}
        plausible_dict = {}
        for eval_name in all_dict.keys():
            bug_eval_re = all_dict.get(eval_name)
            bug_patches = candidate_dict[eval_name]
            simp_id=bugID.replace('qbs_','')
            if simp_id in bug_eval_re.keys():
                bugID=simp_id
            if bugID in bug_eval_re.keys():
                ind = bug_eval_re[bugID]
                candidate = bug_patches[bugID]["patches"][str(ind)]
                plausible_dict[eval_name] = {"manual_check": "None","reason":"None", "pred": candidate.replace('\t', ' ').split('\n')}
        if len(plausible_dict.keys()) > 0:
            check_dict["plausible_patches"] = plausible_dict
            with open(output_dir + '/' + bugID + ".check", 'w', encoding='utf8') as df:
                json.dump(check_dict, df, indent=2)
            print(bugID, "finished")
#preprare_quixbugs_4check(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Quixbugs.json","F:/NPR_DATA0306/Eval_result/qbs/Check",
     #                    buggy_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines",
       #                  fix_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines"
          #               )

def prepare_d4j_4check(d4j_f,output_dir,fix_methods_dir,buggy_lines_dir,fix_lines_dir,buggy_methods_dir):
    d4j_result=json.load(codecs.open(d4j_f,'r',encoding='utf8'))
    d4j_result=d4j_result['d4j']
    Recoder_result=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/Recoder_Benchmark-1650268628.6649077.json",'r',encoding='utf8'))
    SequenceR_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/SequenceR_Benchmark-1650268490.662376.json", 'r', encoding='utf8'))
    Tufano_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/Tufano_Benchmark-1650268533.4012978.json", 'r', encoding='utf8'))
    Codit_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/Codit_Benchmark_2-1650268599.5276675.json", 'r', encoding='utf8'))
    Edits_result=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/Edits_Benchmark-1650630864.2205443.json", 'r', encoding='utf8'))
    CoCoNut_5_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_5_Benchmark-1650376099.3594997.json", 'r', encoding='utf8'))
    CoCoNut_12_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_12_Benchmark-1650376087.5284874.json", 'r', encoding='utf8'))
    CoCoNut_15_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_15_Benchmark-1650456800.067538.json", 'r', encoding='utf8'))
    CoCoNut_21_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_21_Benchmark-1650456861.0396802.json", 'r', encoding='utf8'))
    CoCoNut_32_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_32_Benchmark-1650457145.5165002.json", 'r', encoding='utf8'))
    CoCoNut_33_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_33_Benchmark-1650457176.123485.json", 'r', encoding='utf8'))
    CoCoNut_35_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_35_Benchmark-1650529371.717962.json", 'r', encoding='utf8'))
    CoCoNut_99_result = json.load(codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_99_Benchmark-1650529400.740373.json", 'r', encoding='utf8'))
    CoCoNut_c7_result = json.load(
        codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_c7_Benchmark-1650618407.7282717.json", 'r',
                    encoding='utf8'))
    CoCoNut_c9_result = json.load(
        codecs.open("F:/NPR_DATA0306/Eval_result/d4j/CoCoNut_c9_Benchmark-1650618441.067373.json", 'r',
                    encoding='utf8'))
    candidate_dict={"Recoder":Recoder_result,"SR":SequenceR_result,"Tufano":Tufano_result,"Codit":Codit_result,"CoCoNut5":CoCoNut_5_result,"CoCoNut12":CoCoNut_12_result,"Edits":Edits_result,
                    "CoCoNut15":CoCoNut_15_result,"CoCoNut21":CoCoNut_21_result,"CoCoNut32":CoCoNut_32_result,"CoCoNut33":CoCoNut_33_result,"CoCoNut35":CoCoNut_35_result,
                    "CoCoNut99":CoCoNut_99_result,"CoCoNutC7":CoCoNut_c7_result,"CoCoNutC9":CoCoNut_c9_result}

    for bugName in d4j_result.keys():
        check_dict={"bugName":bugName}
        files=list(d4j_result[bugName].keys())
        hitcount=0
        for file in files:
            check_dict[file]={}
            ids = d4j_result[bugName][file]["ids"]
            if len(ids)==1:
                id=ids[0]
                fix_method=codecs.open(fix_methods_dir+"/d4j_"+id+'.txt','r',encoding='utf8').read().replace('\t',' ').split('\n')
                buggy_line=codecs.open(buggy_lines_dir+'/d4j_'+id+'.txt','r',encoding='utf8').read().strip()
                fix_line=codecs.open(fix_lines_dir+'/d4j_'+id+'.txt','r',encoding='utf8').read().strip()
                buggy_method=codecs.open(buggy_methods_dir+"/d4j_"+id+'.txt','r',encoding='utf8').read().replace('\t',' ').split('\n')
                check_dict[file]["buggymethod"]=buggy_method
                check_dict[file]["fix_method"]=fix_method
                check_dict[file]["buggy_line"] = buggy_line
                check_dict[file]["fix_line"]=fix_line
                plausible_dict={}
                for eval_name in candidate_dict.keys():
                    patch_dict=candidate_dict[eval_name]
                    if bugName in patch_dict.keys():
                        filepath = d4j_result[bugName][file]["java_path"]
                        if eval_name in ["Tufano"]:
                            filepath="/home/gehongliang/Test/Test_Suite2/code"+filepath
                        elif eval_name in ["SR","Edits"]:
                            filepath = "/home/gehongliang/Test/Test_Suite/code" + filepath
                        elif eval_name in ["Recoder"]:
                            filepath = "/home/gehongliang/Test/Test_Suite5/code" + filepath
                        elif eval_name in ["Codit","CoCoNut33"]:
                            filepath = "/home/gehongliang/Test/Test_Suite4/code" + filepath
                        elif eval_name in ["CoCoNut5","CoCoNut35"]:
                            filepath = "/root/ghl/Test_Suite_1/code" + filepath
                        elif eval_name in ["CoCoNut12","CoCoNut99"]:
                            filepath = "/root/ghl/Test_Suite_2/code" + filepath
                        elif eval_name in ["CoCoNut15","CoCoNutC7"]:
                            filepath = "/root/ghl/Test_Suite_3/code" + filepath
                        elif eval_name in ["CoCoNut21","CoCoNutC9"]:
                            filepath = "/root/ghl/Test_Suite_4/code" + filepath
                        elif eval_name in ["CoCoNut32"]:
                            filepath = "/home/gehongliang/Test/Test_Suite3/code" + filepath
                        hitcount+=1

                        plausible_dict[eval_name]={"manual_check": "None","reason":"None","pred":patch_dict[bugName][filepath][0]['fix_method'].replace('\t',' ').split('\n')}
                if len(plausible_dict.keys())>2:
                    check_dict[file]["plausible_patches"]=plausible_dict
            else:
                hitcount=0
                check_dict[file] = {}
                for idx,id in enumerate(ids):

                    fix_method = codecs.open(fix_methods_dir + "/d4j_" + id + '.txt', 'r', encoding='utf8').read().replace(
                        '\t', ' ').split('\n')
                    buggy_line = codecs.open(buggy_lines_dir + '/d4j_' + id + '.txt', 'r', encoding='utf8').read().strip()
                    fix_line = codecs.open(fix_lines_dir + '/d4j_' + id + '.txt', 'r', encoding='utf8').read().strip()
                    buggy_method = codecs.open(buggy_methods_dir + "/d4j_" + id + '.txt', 'r',
                                               encoding='utf8').read().replace('\t', ' ').split('\n')
                    check_dict[file]["buggymethod_"+str(idx)] = buggy_method
                    check_dict[file]["fix_method_"+str(idx)] = fix_method
                    check_dict[file]["buggy_line_"+str(idx)] = buggy_line
                    check_dict[file]["fix_line_"+str(idx)] = fix_line
                    plausible_dict = {}
                    for eval_name in candidate_dict.keys():
                        patch_dict = candidate_dict[eval_name]
                        if bugName in patch_dict.keys():
                            filepath = d4j_result[bugName][file]["java_path"]
                            if eval_name in ["Tufano"]:
                                filepath = "/home/gehongliang/Test/Test_Suite2/code" + filepath
                            elif eval_name in ["SR", "Edits"]:
                                filepath = "/home/gehongliang/Test/Test_Suite/code" + filepath
                            elif eval_name in ["Recoder"]:
                                filepath = "/home/gehongliang/Test/Test_Suite5/code" + filepath
                            elif eval_name in ["Codit", "CoCoNut33"]:
                                filepath = "/home/gehongliang/Test/Test_Suite4/code" + filepath
                            elif eval_name in ["CoCoNut5", "CoCoNut35"]:
                                filepath = "/root/ghl/Test_Suite_1/code" + filepath
                            elif eval_name in ["CoCoNut12", "CoCoNut99"]:
                                filepath = "/root/ghl/Test_Suite_2/code" + filepath
                            elif eval_name in ["CoCoNut15", "CoCoNutC7"]:
                                filepath = "/root/ghl/Test_Suite_3/code" + filepath
                            elif eval_name in ["CoCoNut21", "CoCoNutC9"]:
                                filepath = "/root/ghl/Test_Suite_4/code" + filepath
                            elif eval_name in ["CoCoNut32"]:
                                filepath = "/home/gehongliang/Test/Test_Suite3/code" + filepath
                            hitcount+=1
                            plausible_dict[eval_name+"_"+str(idx)] = {"manual_check": "None","reason":"None","pred":patch_dict[bugName][filepath][idx]['fix_method'].replace('\t', ' ').split(
                                '\n')}
                    if len(plausible_dict.keys()) > 0:

                        check_dict[file]["plausible_patches_"+str(idx)] = plausible_dict
        if hitcount>1:
            with open(output_dir+'/'+bugName+'.check','w',encoding='utf8')as f:
                json.dump(check_dict,f,indent=2)

#prepare_d4j_4check(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\infos.json","F:/NPR_DATA0306/Eval_result/d4j/Check","F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_methods",
                   #buggy_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_lines",
                   #fix_lines_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines",buggy_methods_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods"
                  # )




#Evaluate_Edits_bears(r"F:\NPR_DATA0306\FixResults\Final_Results\Edit_Benchmark.patches",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\bdjar_.sids",
                     #"F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines",r"F:\NPR_DATA0306\Eval_result\diversity\Edits_bdjar.eval")
#Evaluate_Edits(r"F:\NPR_DATA0306\FixResults\Final_Results\diversity(1).patches","F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines",r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval")
#exit(0)
def Evaluation_Codit(results_f,files_f,distances_f,limited_ids_f,output_f):
    lines=readF2L(results_f)
    files=readF2L(files_f)
    limited_ids=readF2L(limited_ids_f)
    np_lines=np.array(lines)
    group_sep=lines[208]
    indices=np.where(np_lines==group_sep)[0]
    inds=indices.tolist()
    inds=[0]+inds
    print(inds)
    fix_dict=dict()

    with open(distances_f, 'r', encoding='utf8') as fp:
        distances = [i for i in csv.reader(fp)]
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

        idx=0

        id = files[id_index].split('\\')[-1].replace('.txt', '')
        check_id=id.split('_')[-1]

        if True:
            str_match=-1

            for fix_line in fl_group:
                if len(fix_line)>2 and (not fix_line=="True") and (not fix_line=="False"):

                    buggy_line=get_tokenized_str(buggy_line)
                    fix_line=get_tokenized_str(fix_line)

                    if label in fix_line:
                        str_match=idx
                        print('str_match',str_match)
                    idx+=1
            fix_dict[id]=str_match
    idx=0
    for dis_list in distances:
        ind=int(dis_list[0])

        id = files[ind].split('\\')[-1].replace('.txt', '')
        if '0' in dis_list:
            fix_dict[id] = dis_list.index('0')
            print(idx)
            idx+=1

    with open(output_f,'w',encoding='utf8')as f:
        json.dump(fix_dict,f,indent=2)
#Evaluation_Codit(r"F:\NPR_DATA0306\FixResults\full_report\details\testdiverse_100.2_200_codit_result.txt",
                 #r"F:\NPR_DATA0306\Processed_Codit_Diversity\test\files.txt",r"F:\NPR_DATA0306\FixResults\full_report\edit_distances\testdiverse_100.2-77-2--100eds.csv",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",
                 #r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval")
#Evaluation_Codit(r"F:\NPR_DATA0306\Bears_pred\full_report\details\bears_trans_100.2_200_codit_result.txt",
                 #r"F:\NPR_DATA0306\Processed_Codit_Bears\test\files.txt",r"F:\NPR_DATA0306\Bears_pred\full_report\edit_distances\bears_trans_100.2-2-2--100eds.csv",r"F:\NPR_DATA0306\Evaluationdata\Benchmark\bdjar.ids",
                 #r"F:\NPR_DATA0306\Eval_result\benchmark_eval\Codit_bears.eval")
#exit(0)
def Evaluate_CoCoNut(pred_f,ids_f,limited_ids_f,output_f,candi_size=100):
    ids=readF2L(ids_f)
    preds=readF2L(pred_f)
    limit_ids=readF2L(limited_ids_f)
    assert len(preds)%(candi_size+2)==0
    correct_num=0
    results_dict={}
    ind_list=list(range(0,len(preds),102))
    #print(ind_list)
    #print(preds[1632:1734])
    corre_set=set()
    for i in ind_list:
        group = preds[i:i+candi_size+2]
        #print(i)
        #print(len(group))
        try:
            sid,src_str=group[0].split('\t')
            tid,tgt_str=group[1].split('\t')
        except:
            results_dict[ids[id]] = -1
            continue
        id=int(sid[2:])
        check_id=ids[id].split('_')[-1]
        if True:
            if src_str.strip()==tgt_str.strip():
                results_dict[ids[id]]=-1
            else:
                skip_flag=False
                for idx,pred in enumerate(group[2:]):
                    new_pred=pred.split('\t')[-1].strip()
                    if not skip_flag:
                        if new_pred==tgt_str.strip():
                            results_dict[ids[id]] = idx
                            correct_num+=1
                            corre_set.add(ids[id])
                            #print(correct_num)
                            skip_flag=True
                if ids[id] not in results_dict.keys():
                    results_dict[ids[id]] = -1
    print(correct_num,'=='*10)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(results_dict,f,indent=2)
        f.close()
    return corre_set

def Evaluate_Recoder(ids_f,fix_dir,label_dir,output_f):
    ids=readF2L(ids_f)
    files=os.listdir(fix_dir)
    result_dict={}
    correct_num=0
    print("Starting evaluating Recoder")
    print(len(ids))
    for id in ids:
        if "bdjar" in ids_f:
            id='bdjar_'+id
        if id+'.fix' in files:
            f=codecs.open(fix_dir+'/'+id+".fix",'r',encoding='utf8')
            fix_dict=json.load(f)
            label=codecs.open(label_dir+'/'+id+'.txt','r',encoding='utf8').read()
            evalresult=hits_ignorespace(fix_dict,label)
            if evalresult>-1 :
                correct_num+=1
                print(correct_num)
            result_dict[id]=evalresult
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(result_dict,f,indent=2)
        f.close()



def Evaluate_simple(ids_f,limited_ids_f,candi_size,preds_f,labels_f,output_f):
    preds=readF2L(preds_f)
    labels=readF2L(labels_f)
    print(len(preds))
    print(len(labels))
    ids=readF2L(ids_f)
    limited_ids=readF2L(limited_ids_f)
    print(len(limited_ids))
    assert len(preds)/candi_size == len(labels)
    result_dict={}
    correct_num=0
    for i in range(len(ids)):
        id = ids[i].split('_')[-1]
        if id in limited_ids:
            current_preds=preds[i*candi_size:(i+1)*candi_size]
            hit_result=hits_normal(current_preds,labels[i])
            if hit_result>-1:
                correct_num+=1
            result_dict[id]=hit_result
        print(i)
    print("correct_num: ",correct_num)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(result_dict,f,indent=2)
        f.close()
    return dict

#Evaluate_simple(r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\Tufano\benchmark.ids",r"F:\NPR_DATA0306\Evaluationdata\Benchmark\bdjar.ids",100,r"F:\NPR_DATA0306\FixResults\Tufano_3\Tufano_3_nb100_benchmark.recovery",
                #"F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/tgtabs/labels.txt","F:/NPR_DATA0306/Eval_result/diversity/Tufano_bdjar.eval")

#Evaluate_simple("F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Tufano/diversity_.ids",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",100,"F:/NPR_DATA0306/FixResults/Tufano_3/Tufano_3_nb100_diversity.recovery",
               #"F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/tgtabs/labels.txt","F:/NPR_DATA0306/Eval_result/diversity/SequenceR_diversity.eval")
           
#Evaluate_simple(r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.sids",100,r"F:\NPR_DATA0306\Bears_pred\SequenceR\SR_26_bears.pred",
                #r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.fix",r"F:\NPR_DATA0306\Bears_pred\SequenceR\SR_26_bears.eval")

#Evaluate_simple(r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\benchmark.sids",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\bdjar_.sids",100,r"F:\NPR_DATA0306\FixResults\Benchmark_SR\21063_SR_26_b100.pred",
                #r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\benchmark.fix","F:/NPR_DATA0306/Eval_result/diversity/SequenceR_bdjar.eval")

#Evaluate_Recoder(ids_f=r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",fix_dir="F:/NPR_DATA0306/FixResults/Recoder_new_diversity/results",
                 #label_dir="F:/NPR_DATA0306/Evaluationdata/Diversity/fix_lines",output_f="F:/NPR_DATA0306/Eval_result/diversity/Recoder_new_diversity.eval")

#Evaluate_Recoder(ids_f=r"F:\NPR_DATA0306\Evaluationdata\Benchmark\bdjar.ids",fix_dir="F:/NPR_DATA0306/Recoder_new/bench_",
                 #label_dir="F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_lines",output_f="F:/NPR_DATA0306/Eval_result/diversity/Recoder_bdjar.eval")

#cor_set1=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_5_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_5.eval")
#cor_set2=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_12_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                         #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_12.eval")
#cor_set3=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_21_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                         # r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_21.eval")
#cor_set4=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_32_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_32.eval")
#cor_set5=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_33_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                         # r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_33.eval")
#cor_set6=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_35_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_35.eval")
#cor_set7=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_15_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_15.eval")
#cor_set8=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_99_save\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_99.eval")
#cor_set9=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_context_tune_7\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_c7.eval")
#cor_set10=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_context_tune_9\pred_100_diversity.txt",r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\CoCoNut\diversity.ids",
                          #r"F:\NPR_DATA0306\Evaluationdata\Diversity-processed\Recoder\final.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_c9.eval")
#cor_set1=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_5_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_5_bdjar.eval")
#cor_set2=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_12_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_12_bdjar.eval")
#cor_set3=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_15_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_15_bdjar.eval")
#cor_set4=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_21_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_21_bdjar.eval")
#cor_set5=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_32_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_32_bdjar.eval")
#cor_set6=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_33_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_33_bdjar.eval")
#cor_set7=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_35_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_35_bdjar.eval")
#cor_set8=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_99_save\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_99_bdjar.eval")
#cor_set9=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_context_tune_7\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                        r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_c7_bdjar.eval")
#cor_set10=Evaluate_CoCoNut(r"F:\NPR_DATA0306\Processed_CoCoNut\CoCoNut_context_tune_9\pred_100_benchmark.txt",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",
  #                       r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\CoCoNut\benchmark.ids",r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_c9_bdjar.eval")
#unionset=set()
#dir="F:/NPR_DATA0306/Bears_pred/"
#sub_dirs=["CoCoNut_5_save","CoCoNut_12_save","CoCoNut_15_save","CoCoNut_21_save","CoCoNut_32_save","CoCoNut_33_save","CoCoNut_35_save","CoCoNut_99_save","CoCoNut_context_tune_7","CoCoNut_context_tune_9"]
#for sub_dir in sub_dirs:
    #eval_result=json.load(codecs.open(dir+'/'+sub_dir+'/pred_bears.eval'))
    #for id in eval_result.keys():
        #if int(eval_result[id])==1:
            #unionset.add(id)

#dict={}
#for id in unionset:
    #dict[id]=1
#with open(r"F:\NPR_DATA0306\Eval_result\benchmark_eval\CoCoNut_union_bears.eval",'w',encoding='utf8')as f:
    #json.dump(dict,f,indent=2)
    #f.close()