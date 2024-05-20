import codecs
import json
import math

def count_total_plausible_num(d4j_result_f):
    result = json.load(codecs.open(d4j_result_f,'r',encoding='utf8'))
    all_count=0
    for bug in result.keys():
        buginfo = result[bug]
        rejected =buginfo["Rejected"]
        accepted=buginfo["Accepted"]
        #all_count+=len(rejected)
        all_count+=len(accepted)
    print(all_count)
count_total_plausible_num(r"D:\文档\icse2023\d4j_result_2.json")
def count_total_fixed(d4j_results_f):
    results=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
    print(len(results.keys()))
    count_dict={}
    fail_count_dict={}
    count_all=0
    for bug in results:
        accepted=results[bug]["Accepted"]
        rejected=results[bug]["Rejected"]
        count_all=len(accepted)+count_all
        count_all=len(rejected)+count_all
        suc_add_already=[]
        fail_add_already=[]
        for re in accepted:
            sys=re["sys"]
            if sys in suc_add_already:
                continue
            if sys in count_dict.keys():
                total=count_dict[sys]
                total=total+1
                count_dict[sys]=total
            else:
                count_dict[sys] = 1
            suc_add_already.append(sys)
        for re in rejected:
            sys=re["sys"]
            if sys in fail_add_already:
                continue
            if sys in fail_count_dict.keys():
                total=fail_count_dict[sys]
                total=total+1
                fail_count_dict[sys]=total
            else:
                fail_count_dict[sys] = 1
            fail_add_already.append(sys)
    print(count_all)
    print(count_dict)
    print(fail_count_dict)
#count_total_fixed(r"D:\文档\icse2023\d4j_result_2.json")
def count_system_fixed(results_f):
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
    def get_fixed_avgrank(ranklist):
        fixed_count=0
        index_sum=0
        for (bug,index) in ranklist:
            fixed_count+=1
            index_sum+=index
        return fixed_count,math.ceil(index_sum/fixed_count)
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
    print("single bugs",singleline_count)
    print(systems)

    for system in systems.keys():
        print(system,get_fixed_avgrank(systems[system]))
#count_system_fixed(r"D:\文档\icse2023\d4j_result_2.json")
