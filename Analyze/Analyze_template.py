import codecs
import json
import pandas as pd
def get_system_fixed_exclude(results_f,exclude_ids):
    results = json.load(codecs.open(results_f, 'r', encoding='utf8'))
    systems={}
    def update_accept(a_list,bugname,index):
        new_list=[]
        added_flag=0
        for (bug,old_index) in a_list:
            #print(bug,old_index)
            if bug==bugname:
                added_flag=1
                #print("equal")
                #print(bug,old_index,index)
                small_index=min(old_index,index)
                new_list.append((bugname,small_index))
            else:
                #print("no equal")
                new_list.append((bug,old_index))
        if added_flag==0:
            new_list.append((bugname,index))
        return new_list
    singleline_count=0
    for bug in results:
        accepted=results[bug]["Accepted"]
        ids=results[bug]["ids"]
        if len(ids)==1:
            singleline_count+=1
        else:
            continue
        if ids[0] not in exclude_ids:
            continue
        for re in accepted:
            sys=re["sys"]
            if sys in systems.keys():
                #print(sys)
                accepted_list=systems[sys]
                #print(accepted_list)
                #print(bug,re["index"])
                new_list=update_accept(accepted_list,bug,re["index"])
                #print(new_list)
                systems.update({sys:new_list})
            else:
                systems[sys]=[(bug,re["index"])]
    return systems
def get_system_fixed_unexclude(results_f,exclude_ids):
    results = json.load(codecs.open(results_f, 'r', encoding='utf8'))
    systems={}
    def update_accept(a_list,bugname,index):
        new_list=[]
        added_flag=0
        for (bug,old_index) in a_list:
            #print(bug,old_index)
            if bug==bugname:
                added_flag=1
                #print("equal")
                #print(bug,old_index,index)
                small_index=min(old_index,index)
                new_list.append((bugname,small_index))
            else:
                #print("no equal")
                new_list.append((bug,old_index))
        if added_flag==0:
            new_list.append((bugname,index))
        return new_list
    singleline_count=0
    for bug in results:
        accepted=results[bug]["Accepted"]
        ids=results[bug]["ids"]
        if len(ids)==1:
            singleline_count+=1
        else:
            continue
        if ids[0] in exclude_ids:
            continue
        for re in accepted:
            sys=re["sys"]
            if sys in systems.keys():
                #print(sys)
                accepted_list=systems[sys]
                #print(accepted_list)
                #print(bug,re["index"])
                new_list=update_accept(accepted_list,bug,re["index"])
                #print(new_list)
                systems.update({sys:new_list})
            else:
                systems[sys]=[(bug,re["index"])]
    return systems
def count_exclude_template(d4j_result_f,bears_result_f,qbs_result_f):
    FP_op=["qbs_62381824123e2a7ca8437117","qbs_62381824123e2a7ca843711d","qbs_62381824123e2a7ca8437125",
           "qbs_62381824123e2a7ca843712f","qbs_62381824123e2a7ca8437133","d4j_61a8cca68009e7c4a5d3d662",
           "d4j_61a8cca68009e7c4a5d3d7f6","d4j_61a8cca68009e7c4a5d3d63b","d4j_61a8cca68009e7c4a5d3d7da",
           "d4j_61a8cca68009e7c4a5d3d848","d4j_61a8cca68009e7c4a5d3d849","d4j_61a8cca68009e7c4a5d3d88d",
           "d4j_61a8cca78009e7c4a5d3d9c6","d4j_61a8cca58009e7c4a5d3d61b","d4j_61a8cca68009e7c4a5d3d728",
           "d4j_61a8cca78009e7c4a5d3d987","d4j_61a8cca68009e7c4a5d3d681","bears_6257cdb15fef470c3d70c286",
           ]
    FP_kw=["d4j_61a8cca68009e7c4a5d3d8ed","d4j_61a8cca78009e7c4a5d3d97a","d4j_61a8cca68009e7c4a5d3d7e5",
           "d4j_61a8cca68009e7c4a5d3d7a8","d4j_61a8cca68009e7c4a5d3d77a","d4j_61a8cca78009e7c4a5d3d96a",
           "bears_6257cdb15fef470c3d70c269",]
    FP_DR=["d4j_61a8cca68009e7c4a5d3d8c0","d4j_61a8cca68009e7c4a5d3d910","d4j_61a8cca68009e7c4a5d3d795",
           "d4j_61a8cca68009e7c4a5d3d80d","d4j_61a8cca78009e7c4a5d3d9fe","d4j_61a8cca78009e7c4a5d3d9ff",
           "d4j_61a8cca78009e7c4a5d3da00","d4j_61a8cca78009e7c4a5d3da01","d4j_61a8cca78009e7c4a5d3da02",
           "d4j_61a8cca78009e7c4a5d3da03","d4j_61a8cca78009e7c4a5d3da04","d4j_61a8cca78009e7c4a5d3da05",
           "d4j_61a8cca78009e7c4a5d3d960","d4j_61a8cca58009e7c4a5d3d5fe","d4j_61a8cca58009e7c4a5d3d600",
           "d4j_61a8cca68009e7c4a5d3d826","d4j_61a8cca68009e7c4a5d3d827","d4j_61a8cca68009e7c4a5d3d828",
           "d4j_61a8cca68009e7c4a5d3d829","d4j_61a8cca68009e7c4a5d3d84d","bears_6257cdb15fef470c3d70c257",
           "bears_6257cdb15fef470c3d70c261","bears_6257cdb05fef470c3d70c051","bears_6257cdb05fef470c3d70c061",
           "bears_6257cdb05fef470c3d70c062","bears_6257cdb15fef470c3d70c198","bears_6257cdb15fef470c3d70c1c1",
           "bears_6257cdb15fef470c3d70c2ad","bears_6257cdb15fef470c3d70c113","bears_6257cdb15fef470c3d70c119",
           "bears_6257cdb15fef470c3d70c11a","bears_6257cdb15fef470c3d70c13c","bears_6257cdb15fef470c3d70c13d",
           "bears_6257cdb15fef470c3d70c13e","bears_6257cdb15fef470c3d70c16d","bears_6257cdb15fef470c3d70c170",
           "bears_6257cdb15fef470c3d70c171","bears_6257cdb15fef470c3d70c172","bears_6257cdb15fef470c3d70c21d",
           "bears_6257cdb15fef470c3d70c28c"
           ]
    FP_NB=["d4j_61a8cca78009e7c4a5d3d997","d4j_61a8cca68009e7c4a5d3d7cd","d4j_61a8cca68009e7c4a5d3d87f","bears_6257cdb05fef470c3d70c058",
           "bears_6257cdb05fef470c3d70c06a","bears_6257cdb15fef470c3d70c0d1","bears_6257cdb15fef470c3d70c0ff",
           "bears_6257cdb15fef470c3d70c100", "bears_6257cdb15fef470c3d70c250"]
    FP_Exp=["qbs_62381824123e2a7ca8437120","qbs_62381824123e2a7ca8437135","qbs_62381824123e2a7ca8437139","qbs_62381824123e2a7ca843713f",
            "d4j_61a8cca68009e7c4a5d3d729","d4j_61a8cca68009e7c4a5d3d63c","bears_6257cdb15fef470c3d70c241"]

    all_exclude=FP_DR+FP_kw+FP_op+FP_NB+FP_Exp
    d4j_systems_fixed=get_system_fixed_exclude(d4j_result_f,all_exclude)
    bears_systems_fixed = get_system_fixed_exclude(bears_result_f, all_exclude)
    qbs_systems_fixed = get_system_fixed_exclude(qbs_result_f, all_exclude)
    all_systems_fixed={}
    for sys in d4j_systems_fixed.keys():
           all_systems_fixed[sys]=len(d4j_systems_fixed[sys])+len(bears_systems_fixed[sys])+len(qbs_systems_fixed[sys])
    for sys in all_systems_fixed.keys():
           print(sys, all_systems_fixed[sys])

def count_coverage_by_APR(APR_fix_f,NPR_fix_f):
    APR_fixes=json.load(codecs.open(APR_fix_f,'r',encoding='utf8'))
    NPR_fixes=pd.read_csv(NPR_fix_f,sep='\t')
    TBAR_fixes=APR_fixes["kPAR"]+APR_fixes["ACS"]+APR_fixes["SimFix"]+APR_fixes["TBar"]+APR_fixes["FixMiner"]+APR_fixes["AVATAR"]
    systems=["Recoder","SequenceR","RewardRepair","CoCoNut","Edits","Tufano","CodeBERT-ft"]
    systems_left={}
    print(NPR_fixes.head())
    for sys in systems:
        fix_list=NPR_fixes[sys]
        left_fix=[]
        cover_fix=[]
        for fix in fix_list:
            print(fix)
            if str(fix).startswith("Chart_") or str(fix).startswith("Closure_") \
                    or str(fix).startswith("Lang_") or str(fix).startswith("Math_") \
                    or str(fix).startswith("Mockito_") or str(fix).startswith("Time_7"):
                if fix not  in TBAR_fixes:
                    left_fix.append(fix)
                else:
                    cover_fix.append(fix)
        systems_left[sys]={"left":left_fix,"covered":cover_fix}
    for sys in systems_left:

        print(sys,str(int(100*len(systems_left[sys]["covered"])/(len(systems_left[sys]["left"])+len(systems_left[sys]["covered"]))))+'%')
    pass

count_coverage_by_APR(r"D:\文档\icse2023\APR_fix.json",r"D:\文档\icse2023\fixed_all.txt")