import codecs
import json
import os

from Utils.CA_Utils import writeL2F


def count_identical_d4j(infos_f,output_f):
    d4j_infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))
    d4j_bugs=d4j_infos['d4j']
    CoCoNut_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/CoCoNut_union.eval",'r',encoding='utf8'))
    Recoder_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/recoder_eval.txt",'r',encoding='utf8'))
    Edits_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Edits.eval",'r',encoding='utf8'))
    Codit_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Codit.eval",'r',encoding='utf8'))
    SequenceR_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/SR.eval",'r',encoding='utf8'))
    Tufano_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Tufano.eval",'r',encoding='utf8'))
    all_evals={"CoCoNut":CoCoNut_eval,"Recoder":Recoder_eval,"Edits":Edits_eval,"Codit":Codit_eval,"SR":SequenceR_eval,"Tufano":Tufano_eval}
    identical_dict={}
    def get_allids(dict):
        ids=[]
        for file in dict.keys():
            ids=ids+dict[file]["ids"]
        return ids
    def check_identical(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
            else:
                result=int(dict[id])
                if result==-1:
                    return False
        return True
    def check_identical_zero(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
            else:
                result=int(dict[id])
                if result==0:
                    return False
        return True
    def check_identical_CoCoNut(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
        return True
    for bug in d4j_bugs:
        identical_dict[bug]=[]
        check_ids=get_allids(d4j_bugs.get(bug))
        for sys in all_evals.keys():
            if sys == "CoCoNut":
                CoCoNut_eval=all_evals[sys]
                result=check_identical_CoCoNut(check_ids,CoCoNut_eval)
                if result==True:
                    ori_list=identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug:ori_list})
            elif sys in ["Recoder","Tufano"]:
                result = check_identical_zero(check_ids, all_evals[sys])
                if result == True:
                    ori_list = identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug: ori_list})
            else:
                result=check_identical(check_ids,all_evals[sys])
                if result==True:
                    ori_list=identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug:ori_list})
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(identical_dict,f,indent=2)
#count_identical_d4j(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\infos.json",r"F:\NPR_DATA0306\Eval_result\d4j\d4j_identical.json")

def count_identical_qbs(infos_f,output_f):
    qbs_infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))

    CoCoNut_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/CoCoNut_union.eval",'r',encoding='utf8'))
    Recoder_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/recoder_eval.txt",'r',encoding='utf8'))
    Edits_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Edits.eval",'r',encoding='utf8'))
    Codit_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Codit.eval",'r',encoding='utf8'))
    SequenceR_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/SR.eval",'r',encoding='utf8'))
    Tufano_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Tufano.eval",'r',encoding='utf8'))
    all_evals={"CoCoNut":CoCoNut_eval,"Recoder":Recoder_eval,"Edits":Edits_eval,"Codit":Codit_eval,"SR":SequenceR_eval,"Tufano":Tufano_eval}
    identical_dict={}

    def check_identical(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
            else:
                result=int(dict[id])
                if result==-1:
                    return False
        return True
    def check_identical_zero(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
            else:
                result=int(dict[id])
                if result==0:
                    return False
        return True
    def check_identical_CoCoNut(ids,dict):
        for id in ids:
            if id not in dict.keys():
                return False
        return True
    for bug_id in qbs_infos.keys():
        identical_dict[bug_id]=[]
        check_ids=[bug_id.replace("qbs_",'')]
        for sys in all_evals.keys():
            if sys == "CoCoNut":
                CoCoNut_eval=all_evals[sys]
                result=check_identical_CoCoNut(check_ids,CoCoNut_eval)
                if result==True:
                    ori_list=identical_dict[bug_id]
                    ori_list.append(sys)
                    identical_dict.update({bug_id:ori_list})
            elif sys in ["Recoder","Tufano"]:
                result = check_identical_zero(check_ids, all_evals[sys])
                if result == True:
                    ori_list = identical_dict[bug_id]
                    ori_list.append(sys)
                    identical_dict.update({bug_id: ori_list})
            else:
                result=check_identical(check_ids,all_evals[sys])
                if result==True:
                    ori_list=identical_dict[bug_id]
                    ori_list.append(sys)
                    identical_dict.update({bug_id:ori_list})
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(identical_dict,f,indent=2)
#count_identical_qbs(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\QuixBugs.json",r"F:\NPR_DATA0306\Eval_result\qbs\qbs_identical.json")

def count_identical_bears(infos_f,output_f):
    bears_infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))
    CoCoNut_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/CoCoNut_union_bears.eval",'r',encoding='utf8'))
    Recoder_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/recoder_eval.txt",'r',encoding='utf8'))
    Edits_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Edits_bears.eval",'r',encoding='utf8'))
    Codit_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Codit_bears.eval",'r',encoding='utf8'))
    SequenceR_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/SR_bears.eval",'r',encoding='utf8'))
    Tufano_eval=json.load(codecs.open("F:/NPR_DATA0306/Eval_result/benchmark_eval/Tufano_bears.eval",'r',encoding='utf8'))
    all_evals = {"CoCoNut": CoCoNut_eval, "Recoder": Recoder_eval, "Edits": Edits_eval, "Codit": Codit_eval,
                 "SR": SequenceR_eval, "Tufano": Tufano_eval}
    identical_dict = {}

    def get_allids(dict):

        return list(dict.keys())

    def check_identical(ids, dict):
        for id in ids:
            id=id.replace("bears_",'')
            if id not in dict.keys():
                return False
            else:
                result = int(dict[id])
                if result == -1:
                    return False
        return True

    def check_identical_zero(ids, dict):
        for id in ids:
            id = id.replace("bears_", '')
            if id not in dict.keys():
                return False
            else:
                result = int(dict[id])
                if result == 0:
                    return False
        return True

    def check_identical_CoCoNut(ids, dict):
        for id in ids:
            id = id.replace("bears_", '')
            if id not in dict.keys():
                return False
        return True

    for bug in bears_infos.keys():
        identical_dict[bug] = []
        check_ids = get_allids(bears_infos.get(bug))
        for sys in all_evals.keys():
            if sys == "CoCoNut":
                CoCoNut_eval = all_evals[sys]
                result = check_identical_CoCoNut(check_ids, CoCoNut_eval)
                if result == True:
                    ori_list = identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug: ori_list})
            elif sys in ["Recoder"]:
                result = check_identical_zero(check_ids, all_evals[sys])
                if result == True:
                    ori_list = identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug: ori_list})
            else:
                result = check_identical(check_ids, all_evals[sys])
                if result == True:
                    ori_list = identical_dict[bug]
                    ori_list.append(sys)
                    identical_dict.update({bug: ori_list})
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(identical_dict, f, indent=2)
#count_identical_bears(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bears.json","F:/NPR_DATA0306/Eval_result/bears/bears_identical.json")
def correct_d4j(manual_check_dir,output_dir):
    bugs=os.listdir(manual_check_dir)
    correct_count={}
    plausible_count={}
    one_file_auto_error=[]
    multi_files=[]
    for bug in bugs:
        bugname=bug.replace('.check','')
        correct_count[bugname]=[]
        plausible_count[bugname]=[]
        bug_check=json.load(codecs.open(manual_check_dir+'/'+bug,'r',encoding='utf8'))
        filekeys=[]
        for key in bug_check.keys():
            if str(key).endswith(".java"):
                filekeys.append(key)
        if len(filekeys)==1:
            filekey=filekeys[0]
            print("one file change",bugname)
            try:
                plausible_patches = bug_check[filekey]["plausible_patches"]
            except:
                one_file_auto_error.append(bugname)
            for sys in plausible_patches:
                mc=plausible_patches[sys]['manual_check']
                pl_list=plausible_count[bugname]
                pl_list.append(sys)
                plausible_count.update({bugname:pl_list})
                if mc=="correct" or mc == "Correct" or mc=="true":
                    cr_list=correct_count[bugname]
                    cr_list.append(sys)
                    correct_count.update({bugname:cr_list})
        else:
            multi_files.append(bugname)
    with open(output_dir+'/d4j_correct.json','w',encoding='utf8')as f:
        json.dump(correct_count,f,indent=2)
        f.close()
    with open(output_dir+'/d4j_plausible.json','w',encoding='utf8')as f:
        json.dump(plausible_count, f, indent=2)
        f.close()
    print(one_file_auto_error)
    print(multi_files)
def correct_bears(manual_check_dir,output_dir):
    bugs=os.listdir(manual_check_dir)
    correct_count={}
    plausible_count={}
    loss_bugs=[]
    for bug in bugs:
        bugname=bug.replace('.check','')
        correct_count[bugname]=[]
        plausible_count[bugname]=[]

        bug_check=json.load(codecs.open(manual_check_dir+'/'+bug,'r',encoding='utf8'))
        if "plausible_patches" in bug_check.keys():
            plausible_patches=bug_check["plausible_patches"]
            for sys in plausible_patches:
                mc = plausible_patches[sys]['manual_check']
                pl_list = plausible_count[bugname]
                pl_list.append(sys)
                plausible_count.update({bugname: pl_list})
                if mc == "correct" or mc == "Correct" or mc == "true":
                    cr_list = correct_count[bugname]
                    cr_list.append(sys)
                    correct_count.update({bugname: cr_list})
        else:
            loss_bugs.append(bug)
    with open(output_dir+'/bears_correct.json','w',encoding='utf8')as f:
        json.dump(correct_count,f,indent=2)
        f.close()
    with open(output_dir+'/bears_plausible.json','w',encoding='utf8')as f:
        json.dump(plausible_count, f, indent=2)
        f.close()
    print(loss_bugs)
#correct_bears("F:/NPR_DATA0306/Eval_result/bears/manual_check","F:/NPR_DATA0306/Eval_result/bears")
def correct_qbs(manual_check_dir,output_dir):
    bugs=os.listdir(manual_check_dir)
    correct_count={}
    plausible_count={}
    one_file_auto_error=[]
    multi_files=[]
    for bug in bugs:
        bugname=bug.replace('.check','')
        correct_count[bugname]=[]
        plausible_count[bugname]=[]
        print(bug)
        bug_check=json.load(codecs.open(manual_check_dir+'/'+bug,'r',encoding='utf8'))
        plausible_patches=bug_check["plausible_patches"]
        for sys in plausible_patches.keys():
            mc = plausible_patches[sys]['manual_check']
            pl_list = plausible_count[bugname]
            pl_list.append(sys)
            plausible_count.update({bugname: pl_list})
            if mc == "correct" or mc == "Correct" or mc == "true":
                cr_list = correct_count[bugname]
                cr_list.append(sys)
                correct_count.update({bugname: cr_list})

    with open(output_dir+'/qbs_correct.json','w',encoding='utf8')as f:
        json.dump(correct_count,f,indent=2)
        f.close()
    with open(output_dir+'/qbs_plausible.json','w',encoding='utf8')as f:
        json.dump(plausible_count, f, indent=2)
        f.close()
    print(one_file_auto_error)
    print(multi_files)
#correct_qbs("F:/NPR_DATA0306/Eval_result/qbs/manual_check","F:/NPR_DATA0306/Eval_result/qbs")

#correct_d4j("F:/NPR_DATA0306/Eval_result/d4j/manual_check","F:/NPR_DATA0306/Eval_result/d4j")

def get_all_result(correct_json,plausible_json,identical_json):
    correct_result=json.load(codecs.open(correct_json,'r',encoding='utf8'))
    plausible_result=json.load(codecs.open(plausible_json,'r',encoding='utf8'))
    identical_result=json.load(codecs.open(identical_json,'r',encoding='utf8'))
    correct_count={"Recoder":[],"CoCoNut":[],"SR":[],"Tufano":[],"Edits":[],"Codit":[]}
    identical_count={"Recoder":[],"CoCoNut":[],"SR":[],"Tufano":[],"Edits":[],"Codit":[]}
    plausible_count = {"Recoder": [], "CoCoNut": [], "SR": [], "Tufano": [], "Edits": [], "Codit": []}
    for key in plausible_result.keys():
        for sys in plausible_result[key]:
            if str(sys).startswith("CoCoNut"):
                ori_list=plausible_count["CoCoNut"]
                ori_list.append(key)
                plausible_count.update({"CoCoNut":ori_list})
            else:
                ori_list = plausible_count[sys]
                ori_list.append(key)
                plausible_count.update({sys:ori_list})
    for key in identical_result.keys():
        for sys in identical_result[key]:
            if str(sys).startswith("CoCoNut"):
                ori_list=correct_count["CoCoNut"]
                ori_list.append(key)
                correct_count.update({"CoCoNut":ori_list})
                ori_list2 = plausible_count["CoCoNut"]
                ori_list2.append(key)
                plausible_count.update({"CoCoNut": ori_list2})
                ori_list3 = identical_count["CoCoNut"]
                ori_list3.append(key)
                identical_count.update({"CoCoNut": ori_list3})
            else:
                ori_list = correct_count[sys]
                ori_list.append(key)
                correct_count.update({sys:ori_list})
                ori_list2 = plausible_count[sys]
                ori_list2.append(key)
                plausible_count.update({sys: ori_list2})
                ori_list3 = identical_count[sys]
                ori_list3.append(key)
                identical_count.update({sys: ori_list3})

    for key in correct_result.keys():
        for sys in correct_result[key]:
            if str(sys).startswith("CoCoNut"):
                ori_list=correct_count["CoCoNut"]
                ori_list.append(key)
                correct_count.update({"CoCoNut":ori_list})
                ori_list2 = plausible_count["CoCoNut"]
                ori_list2.append(key)
                plausible_count.update({"CoCoNut": ori_list2})
            else:
                ori_list = correct_count[sys]
                ori_list.append(key)
                correct_count.update({sys:ori_list})
                ori_list2 = plausible_count[sys]
                ori_list2.append(key)
                plausible_count.update({sys: ori_list2})
    for key in correct_count.keys():
        print(key,len(set(correct_count[key])))
    print('------------------------------')
    for key in identical_count.keys():
        print(key,len(set(identical_count[key])))
    print('------------------------------')
    for key in plausible_count.keys():
        print(key,len(set(plausible_count[key])))

    correct_set=set()
    plausible_set=set()
    for val_list in correct_count.values():
        for val in val_list:
            correct_set.add(val)
    print(len(correct_set))
    for val_list in plausible_count.values():
        for val in val_list:
            plausible_set.add(val)
    print(len(plausible_set))


def count_Diversity():
    CoCoNut_eval=json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval"))
    Edits_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval"))
    Recoder_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_new_diversity.eval"))
    SequenceR_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval"))
    Tufano_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_diversity.eval"))
    Codit_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval"))
    dict={"CoCoNut":CoCoNut_eval,"Edits":Edits_eval,"Recoder":Recoder_eval,"SequenceR":SequenceR_eval,"Tufano":Tufano_eval,"Codit":Codit_eval}
    hit_dict = {"CoCoNut": set(), "Edits": set(), "Recoder": set(), "SequenceR": set(),
            "Tufano": set(), "Codit": set()}
    for key in dict.keys():
        count=0
        evals=dict.get(key)
        for id in evals.keys():
            value=int(evals[id])
            if value >-1:
                ori_set=hit_dict.get(key)
                ori_set.add(id)
                hit_dict.update({key:ori_set})
                count+=1
        print(key,count)
    all_unique=list(hit_dict["CoCoNut"]|hit_dict["Edits"]|hit_dict["Recoder"]|hit_dict["SequenceR"]|hit_dict["Tufano"]|hit_dict["Codit"])
    writeL2F(all_unique,"F:/NPR_DATA0306/Analyze/distance/correct.ids")
def count_Diversity_unique_rate():
    CoCoNut_eval=json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval"))
    Edits_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval"))
    Recoder_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_new_diversity.eval"))
    SequenceR_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval"))
    Tufano_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_diversity.eval"))
    Codit_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval"))
    dict={"CoCoNut":CoCoNut_eval,"Edits":Edits_eval,"Recoder":Recoder_eval,"SequenceR":SequenceR_eval,"Tufano":Tufano_eval,"Codit":Codit_eval}
    hit_dict = {"CoCoNut": set(), "Edits": set(), "Recoder": set(), "SequenceR": set(),
            "Tufano": set(), "Codit": set()}
    for key in dict.keys():
        count=0
        evals=dict.get(key)
        for id in evals.keys():
            value=int(evals[id])
            if value >-1:
                ori_set=hit_dict.get(key)
                ori_set.add(id)
                hit_dict.update({key:ori_set})
                count+=1
        print(key,count)
    for key in hit_dict.keys():
        first_sys=key
        first_fix=hit_dict.get(first_sys)
        unique_fix=first_fix
        for sec_sys in hit_dict.keys():
            if sec_sys==first_sys:
                pass
            else:
                sec_fix=hit_dict[sec_sys]
                unique_fix=unique_fix-sec_fix
                overlap_fix=len(first_fix&sec_fix)
                overlap_rate=str(int(overlap_fix*100/len(first_fix)))+'%'
                print(first_sys,sec_sys,overlap_fix,overlap_rate)
        print(first_sys,"unique",len(unique_fix),len(unique_fix)/len(first_fix))
#count_Diversity_unique_rate()
count_Diversity()
def count_bdjar():
    CoCoNut_eval=json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_bdjar.pure.eval"))
    Edits_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Edits_bdjar.pure.eval"))
    Recoder_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_bdjar.pure.eval"))
    SequenceR_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_bdjar.pure.eval"))
    Tufano_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_bdjar.pure.eval"))
    Codit_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_bdjar.pure.eval"))
    dict={"CoCoNut":CoCoNut_eval,"Edits":Edits_eval,"Recoder":Recoder_eval,"SequenceR":SequenceR_eval,"Tufano":Tufano_eval,"Codit":Codit_eval}
    hit_dict = {"CoCoNut": set(), "Edits": set(), "Recoder": set(), "SequenceR": set(),
            "Tufano": set(), "Codit": set()}
    for key in dict.keys():
        count=0
        evals=dict.get(key)
        for id in evals.keys():
            value=int(evals[id])
            if value >-1:
                ori_set=hit_dict.get(key)
                ori_set.add(id)
                hit_dict.update({key:ori_set})
                count+=1
        print(key,count)
    all_unique=len(hit_dict["CoCoNut"]|hit_dict["Edits"]|hit_dict["Recoder"]|hit_dict["SequenceR"]|hit_dict["Tufano"]|hit_dict["Codit"])
    print(all_unique)
#count_bdjar()
def get_pure_bdjar(bdjar_f,branch_f):
    bdjar_dict=json.load(codecs.open(bdjar_f,'r',encoding='utf8'))
    print(len(bdjar_dict.keys()))
    branch_dict=json.load(codecs.open(branch_f,'r',encoding='utf8'))
    for branch in branch_dict.keys():
        ids=branch_dict[branch]
        if len(ids)>1:
            del_ids=ids[1:]
            for did in del_ids:
                if did in bdjar_dict.keys():
                    del bdjar_dict[did]
    print(len(bdjar_dict.keys()))
    with open(bdjar_f+'.pure','w',encoding='utf8')as f:
        json.dump(bdjar_dict,f,indent=2)
#get_pure_bdjar(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bdjar.json",r"F:\NPR_DATA0306\Evaluationdata\Benchmark\branch2bug.json")

#get_all_result(r"F:\NPR_DATA0306\Eval_result\qbs\qbs_correct.json",r"F:\NPR_DATA0306\Eval_result\qbs\qbs_plausible.json",r"F:\NPR_DATA0306\Eval_result\qbs\qbs_identical.json")
#get_all_result(r"F:\NPR_DATA0306\Eval_result\bears\bears_correct.json",r"F:\NPR_DATA0306\Eval_result\bears\bears_plausible.json",r"F:\NPR_DATA0306\Eval_result\bears\bears_identical.json")

#get_d4j_all_result(r"F:\NPR_DATA0306\Eval_result\d4j\d4j_correct.json",r"F:\NPR_DATA0306\Eval_result\d4j\d4j_plausible.json",r"F:\NPR_DATA0306\Eval_result\d4j\d4j_identical.json")