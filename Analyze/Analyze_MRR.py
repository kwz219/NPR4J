import codecs
import json
import math


def get_system_fixed(results_f):
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
def get_MRR_sum(systems):
    sum_systems={}
    for sys in systems:
        sum=0
        fixlist=systems[sys]
        for fix in fixlist:
            index=int(fix[1])
            sum+=(1/index)
        sum_systems[sys]=sum
    return sum_systems

def calculate_MRR(d4j_results_f,bears_results_f,qbs_results_f):
    systems_d4j=get_system_fixed(d4j_results_f)
    systems_bears=get_system_fixed(bears_results_f)
    systems_qbs=get_system_fixed(qbs_results_f)
    sum_all={}
    sum_d4j=get_MRR_sum(systems_d4j)
    sum_qbs=get_MRR_sum(systems_qbs)
    sum_bears=get_MRR_sum(systems_bears)
    for sys in sum_d4j.keys():
        sum_all[sys]=sum_d4j[sys]+sum_qbs[sys]+sum_bears[sys]
    for sys in sum_all:
        print(sys,sum_all[sys]/330)
