import codecs
import json



def Analyze_Plausible_top_k(d4j_results_f,top_k=1000):
    plausible_all={}
    systems_fixed=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
    for bug in systems_fixed.keys():
        bug_info=systems_fixed[bug]
        ids=bug_info["ids"]
        if len(ids)>=1:
            Accepted=bug_info["Accepted"]
            Rejected=bug_info["Rejected"]
            for re in Accepted:
                sys=re["sys"]
                if sys in plausible_all.keys():
                    all_dict=plausible_all[sys][bug] if bug in plausible_all[sys].keys() else {"accept":[],"reject":[]}
                    accepted_list=all_dict["accept"]
                    accepted_list.append(re)
                    all_dict["accept"]=accepted_list
                    plausible_all[sys][bug]=all_dict
                else:
                    all_dict={bug:{"accept":[re],"reject":[]}}
                    plausible_all[sys]=all_dict
            for re in Rejected:
                sys=re["sys"]
                if sys in plausible_all.keys():
                    all_dict = plausible_all[sys][bug] if bug in plausible_all[sys].keys() else {"accept":[],"reject":[]}
                    reject_list=all_dict["reject"]
                    reject_list.append(re)
                    all_dict["reject"]=reject_list
                    plausible_all[sys][bug]=all_dict
                else:
                    all_dict={bug:{"accept":[],"reject":[re]}}
                    plausible_all[sys]=all_dict
    #print(top_k)
    sys_plausible={}
    for sys in plausible_all.keys():
        all_info=plausible_all[sys]
        #print(all_info)
        plausbile_count=0
        correct_count=0
        all_correct=0
        for bug in all_info.keys():
            plausible_info=all_info[bug]
            #print(plausible_info)
            #print(bug)
            accepted=plausible_info["accept"]
            if len(accepted)>0:
                all_correct+=1
            rejected=plausible_info["reject"]
            marked_accepted=[]
            for re in accepted:
                re["status"]="accept"
                marked_accepted.append(re)
            marked_rejected=[]
            for re in rejected:
                re["status"]="reject"
                marked_rejected.append(re)
            all=marked_rejected+marked_accepted
            sorted_all=sorted(all, key=lambda x: x["index"])
            #print(sorted_all)
            #print(bug,sorted_all)
            #print(len(sorted_all))
            #print(top_k)
            k=min(len(sorted_all),top_k)


            temp_reject=0
            temp_accept=0
            for ind in range(k):
                fix_re=sorted_all[ind]["status"]
                if fix_re=="accept":
                    temp_accept+=1
                    break
                else:
                    temp_reject+=1
            plausbile_count=plausbile_count+temp_reject+temp_accept
            correct_count=correct_count+temp_accept
        sys_plausible[sys]={"plausible":plausbile_count,"correct":correct_count}
        print(sys,str(correct_count)+'/'+str(plausbile_count))
    return sys_plausible

def get_first_fixed(fix_list):
    system_first={}
    for item in fix_list:
        sys=item["sys"]
        index=item["index"]
        if sys in system_first.keys():
            old_index=system_first[sys]
            new_index=min(old_index,index)
            system_first[sys]=new_index
        else:
            system_first[sys]=index
    return system_first
def prepare_plausible_data_4box(d4j_results_f,qbs_results_f,bears_results_f,output_f):
    d4j_fixed=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
    qbs_fixed=json.load(codecs.open(qbs_results_f,'r',encoding='utf8'))
    bears_fixed=json.load(codecs.open(bears_results_f,'r',encoding='utf8'))
    head_line=["Bug","Edits","Tufano","CoCoNut","CodeBERT-ft","RewardRepair","Recoder","SequenceR","Recoder_ori",
               "RewardRepair_ori"]

    all_list=["Bug","Edits","Tufano","CoCoNut","CodeBERT-ft","RewardRepair","Recoder","SequenceR","Recoder_ori",
               "RewardRepair_ori"]
    all_list.append(','.join(head_line))
    for bug in d4j_fixed.keys():
        bug_info=d4j_fixed[bug]
        ids=bug_info["ids"]
        bug_fix_list=[bug]+["" for i in range(9)]
        skipflag=0
        if len(ids)==1:
            accepted_list=bug_info["Accepted"]
            if len(accepted_list)>0:
                #print(accepted_list)
                first_fixed=get_first_fixed(accepted_list)
                reject_list=bug_info["Rejected"]
                for sys in first_fixed.keys():
                    sys_ind=head_line.index(sys)
                    bug_fix_list[sys_ind]="1"

                for item in reject_list:
                    sys = item["sys"]
                    index = item["index"]
                    sys_index=head_line.index(sys)
                    if sys in first_fixed.keys():
                        if index < first_fixed[sys]:

                            if bug_fix_list[sys_index]=="":
                                bug_fix_list[sys_index]="1"
                            else:
                                bug_fix_list[sys_index]=str(int(bug_fix_list[sys_index])+1)
        if not skipflag==1:
            all_list.append(','.join(bug_fix_list))
    for bug in qbs_fixed.keys():
        bug_info=qbs_fixed[bug]
        ids=bug_info["ids"]
        bug_fix_list=[bug]+["" for i in range(9)]
        skipflag = 0
        if len(ids)==1:
            if len(accepted_list) > 0:
                accepted_list=bug_info["Accepted"]
                first_fixed=get_first_fixed(accepted_list)
                reject_list=bug_info["Rejected"]
                for sys in first_fixed.keys():
                    sys_ind=head_line.index(sys)
                    bug_fix_list[sys_ind]="1"

                for item in reject_list:
                    sys = item["sys"]
                    index = item["index"]
                    sys_index=head_line.index(sys)
                    if sys in first_fixed.keys():
                        if index < first_fixed[sys]:

                            if bug_fix_list[sys_index]=="":
                                bug_fix_list[sys_index]="1"
                            else:
                                bug_fix_list[sys_index]=str(int(bug_fix_list[sys_index])+1)
        if skipflag==0:
            all_list.append(','.join(bug_fix_list))
    for bug in bears_fixed.keys():
        bug_info=bears_fixed[bug]
        ids=bug_info["ids"]
        bug_fix_list=[bug]+["" for i in range(9)]
        skipflag = 0
        if len(ids)==1:
            accepted_list=bug_info["Accepted"]
            if len(accepted_list) > 0:
                first_fixed=get_first_fixed(accepted_list)
                reject_list=bug_info["Rejected"]
                for sys in first_fixed.keys():
                    sys_ind = head_line.index(sys)
                    bug_fix_list[sys_ind] = "1"

                for item in reject_list:
                    sys = item["sys"]
                    index = item["index"]
                    sys_index=head_line.index(sys)
                    if sys in first_fixed.keys():
                        if index < first_fixed[sys]:

                            if bug_fix_list[sys_index]=="":
                                bug_fix_list[sys_index]="1"
                            else:
                                bug_fix_list[sys_index]=str(int(bug_fix_list[sys_index])+1)
        if not skipflag==1:
            all_list.append(','.join(bug_fix_list))

    with open(output_f,'w',encoding='utf8')as f:
        for line in all_list:
            f.write(line+'\n')
        f.close()

def prepare_data_4line(d4j_results_f,qbs_results_f,bears_results_f,output_f):
    all_lines=[]
    systems=["Edits","Tufano","CoCoNut","CodeBERT-ft","RewardRepair","Recoder","SequenceR","Recoder_ori",
               "RewardRepair_ori"]

    sys_content={}
    for sys in systems:
        sys_content[sys]=['' for i in range(191)]
    header_line=[str(i) for i in range(0,191)]
    all_lines.append(','.join(header_line))
    for k in range(1,191):
        d4j_pcount=Analyze_Plausible_top_k(d4j_results_f,k)
        qbs_pcount=Analyze_Plausible_top_k(qbs_results_f,k)
        bears_pcount=Analyze_Plausible_top_k(bears_results_f,k)
        for sys in sys_content.keys():
            old_list=sys_content[sys]
            old_list[k]=str(round((d4j_pcount[sys]["plausible"]+qbs_pcount[sys]["plausible"]+bears_pcount[sys]["plausible"])/(d4j_pcount[sys]["correct"]+qbs_pcount[sys]["correct"]+bears_pcount[sys]["correct"]),2))
            sys_content[sys]=old_list
    for sys in sys_content.keys():
        list=sys_content[sys]
        list[0]=sys
        all_lines.append(','.join(list))
    with open(output_f,'w',encoding='utf8')as f:
        for line in all_lines:
            f.write(line+'\n')
        f.close()




