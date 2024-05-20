import codecs
import json
import pandas as pd

def statistics_d4j(d4j_infos_f,results_f,output_f):
    infos_dict=json.load(codecs.open(d4j_infos_f,'r',encoding='utf8'))["d4j"]
    results_dict={}
    not_fixed_bugs=['Closure-165', 'JacksonDatabind-103', 'Closure-155', 'Closure-134', 'Closure-34', 'JxPath-13', 'JacksonDatabind-38', 'Cli-39', 'Jsoup-87', 'JacksonDatabind-10', 'Closure-90', 'JacksonCore-12', 'Math-18', 'Closure-147', 'Closure-169', 'JacksonDatabind-15', 'Mockito-17', 'Closure-157', 'JacksonDatabind-52', 'Closure-27', 'Compress-47', 'JxPath-16', 'Closure-108', 'Closure-148', 'Mockito-14', 'Closure-72', 'Mockito-11', 'Closure-144', 'Jsoup-92', 'Closure-37', 'Chart-18', 'Mockito-23', 'JxPath-20', 'Time-26', 'Gson-4', 'JacksonDatabind-55', 'Math-83', 'Closure-149', 'Closure-163', 'Lang-32', 'Closure-167', 'Math-100', 'Cli-31', 'Closure-89', 'JacksonDatabind-31', 'JacksonDatabind-95', 'Closure-30', 'Math-81', 'JacksonCore-17', 'Closure-100', 'Chart-22', 'JacksonCore-24', 'Math-47', 'Cli-1', 'Cli-13', 'JacksonDatabind-53', 'JacksonDatabind-65', 'JacksonDatabind-73', 'Closure-75', 'JacksonDatabind-14', 'Lang-36', 'Lang-15', 'Cli-33', 'Closure-9', 'Mockito-4', 'Cli-18', 'Math-65', 'JacksonDatabind-108', 'Math-62']
    for bug in infos_dict:
        if bug.replace('_','-') in not_fixed_bugs:
            continue

        bug_info=infos_dict[bug]
        ids=[]
        #print(bug_info)
        for file in bug_info.keys():
            ids+=bug_info[file]["ids"]
        if len(ids)>1:
            continue
        results_dict[bug]={"ids":["d4j_"+id for id in ids],"Rejected":[],"Accepted":[]}
        #print(results_dict[bug])


    results_all=pd.read_excel(results_f,sheet_name="检查列表")

    multi_flag=0
    Accepted=True
    add_count=0
    for index,row in results_all.iterrows():
        bugname=row["Bug-Name"]
        #print(results_dict[bugname]["ids"])
        #print(type(bugname))
        if isinstance(bugname,float):
            bugname=last_bug_name
        if bugname.replace('_','-') in not_fixed_bugs or (not bugname in results_dict.keys()):
            continue
        multi_position=len(results_dict[bugname]["ids"])>1
        #print(multi_position)
        system=row["NPR-System"]
        patchindex=row["Patch-Index"]
        check1=row["Checker1"]
        check2=row["Checker2"]
        check3=row["Checker3"]

        if multi_position:

            if check1 == "Reject" or check2 == "Reject" or check3 == "Reject":
                Accepted= False
            else:
                Accepted=Accepted and True
            #print(Accepted)
            multi_flag+=1
            if multi_flag==len(results_dict[bugname]["ids"]):
                if Accepted:
                    bug_accepted_list = results_dict[bugname]["Accepted"]
                    bug_accepted_list.append({"sys": system, "index": str(patchindex).replace('[','').replace(']',''), "LineId": index})
                    results_dict[bugname]["Accepted"] = bug_accepted_list
                    add_count+=1
                else:
                    bug_rejected_list = results_dict[bugname]["Rejected"]
                    bug_rejected_list.append({"sys": system, "index": str(patchindex).replace('[','').replace(']',''), "LineId": index})
                    results_dict[bugname]["Rejected"] = bug_rejected_list
                    add_count += 1
                multi_flag=0
                Accepted=True

        else:
            if check1=="Reject" or check2=="Reject" or check3=="Reject":
                bug_rejected_list = results_dict[bugname]["Rejected"]
                bug_rejected_list.append({"sys":system,"index":int(str(patchindex).replace('[','').replace(']','')),"LineId":index})
                results_dict[bugname]["Rejected"]=bug_rejected_list
                add_count += 1
            else:
                bug_accepted_list=results_dict[bugname]["Accepted"]
                bug_accepted_list.append({"sys":system,"index":int(str(patchindex).replace('[','').replace(']','')),"LineId":index})
                results_dict[bugname]["Accepted"]=bug_accepted_list
                add_count += 1
        last_bug_name=bugname
        #print(index)
    count_all=0
    for bug in results_dict:
        accepted=results_dict[bug]["Accepted"]
        rejected=results_dict[bug]["Rejected"]
        count_all=len((accepted))+count_all
        count_all=len((rejected))+count_all
    print(count_all)
    print(add_count)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(results_dict,f,indent=2)
statistics_d4j(r"D:\Test_Suite_Ori\Defects4J_Test\config\infos.json",r"D:\文档\icse2023\defects4j-plausible-check-latest.xlsx","D:\文档\icse2023\d4j_result_2.json")
def statistics_quixbugs(qbs_infos_f,results_f,output_f):
    qbs_infos=json.load(codecs.open(qbs_infos_f,'r',encoding='utf8'))
    results_all = pd.read_excel(results_f, sheet_name="检查列表")
    results_dict = {}
    for id in qbs_infos.keys():
        buginfo=qbs_infos[id]
        bugname=buginfo["name"]
        results_dict[bugname]={"ids":[id],"Rejected":[],"Accepted":[]}
    print(results_dict)
    for index, row in results_all.iterrows():
        bugname = row["Bug-Name"]
        system=row["NPR-System"]
        patchindex=row["Patch-Index"]
        check1=row["Checker1"]
        check2=row["Checker2"]
        check3=row["Checker3"]
        if check1 == "Reject" or check2 == "Reject" or check3 == "Reject":
            bug_rejected_list = results_dict[bugname]["Rejected"]
            bug_rejected_list.append(
                {"sys": system, "index": int(str(patchindex).replace('[', '').replace(']', '')), "LineId": index})
            results_dict[bugname]["Rejected"] = bug_rejected_list

        else:
            bug_accepted_list = results_dict[bugname]["Accepted"]
            bug_accepted_list.append(
                {"sys": system, "index": int(str(patchindex).replace('[', '').replace(']', '')), "LineId": index})
            results_dict[bugname]["Accepted"] = bug_accepted_list
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(results_dict,f,indent=2)
#statistics_quixbugs("D:/QuixBugs.json",r"D:\文档\icse2023\QuixBugs补丁检查.xlsx",r"D:\文档\icse2023\qbs_result.json")
def statistics_bears(bears_infos_f,results_f,output_f):
    infos_dict=json.load(codecs.open(bears_infos_f,'r',encoding='utf8'))
    results_dict={}
    for bug in infos_dict:
        bug_info=infos_dict[bug]
        ids=[]
        #print(bug_info)
        for id in bug_info.keys():
            ids.append(id)

        results_dict[bug]={"ids":ids,"Rejected":[],"Accepted":[]}
        #print(results_dict[bug])
    results_all=pd.read_excel(results_f,sheet_name="检查列表")

    multi_flag=0
    Accepted=True
    add_count=0
    for index,row in results_all.iterrows():
        bugname=row["Bug-Name"]
        #print(results_dict[bugname]["ids"])
        print(type(bugname))
        if isinstance(bugname,float):
            bugname=last_bug_name
        multi_position=len(results_dict[bugname]["ids"])>1
        print(multi_position)
        system=row["NPR-System"]
        patchindex=row["Patch-Index"]
        check1=row["Checker1"]
        check2=row["Checker2"]
        check3=row["Checker3"]
        if multi_position:

            if check1 == "Reject" or check2 == "Reject" or check3 == "Reject":
                Accepted= False
            else:
                Accepted=Accepted and True
            print(Accepted)
            multi_flag+=1
            if multi_flag==len(results_dict[bugname]["ids"]):
                if Accepted:
                    bug_accepted_list = results_dict[bugname]["Accepted"]
                    bug_accepted_list.append({"sys": system, "index": str(patchindex).replace('[','').replace(']',''), "LineId": index})
                    results_dict[bugname]["Accepted"] = bug_accepted_list
                    add_count+=1
                else:
                    bug_rejected_list = results_dict[bugname]["Rejected"]
                    bug_rejected_list.append({"sys": system, "index": str(patchindex).replace('[','').replace(']',''), "LineId": index})
                    results_dict[bugname]["Rejected"] = bug_rejected_list
                    add_count += 1
                multi_flag=0
                Accepted=True

        else:
            if check1=="Reject" or check2=="Reject" or check3=="Reject":
                bug_rejected_list = results_dict[bugname]["Rejected"]
                bug_rejected_list.append({"sys":system,"index":int(str(patchindex).replace('[','').replace(']','')),"LineId":index})
                results_dict[bugname]["Rejected"]=bug_rejected_list
                add_count += 1
            else:
                bug_accepted_list=results_dict[bugname]["Accepted"]
                bug_accepted_list.append({"sys":system,"index":int(str(patchindex).replace('[','').replace(']','')),"LineId":index})
                results_dict[bugname]["Accepted"]=bug_accepted_list
                add_count += 1
        last_bug_name=bugname
        print(index)
    count_all=0
    for bug in results_dict:
        accepted=results_dict[bug]["Accepted"]
        rejected=results_dict[bug]["Rejected"]
        count_all=len((accepted))+count_all
        count_all=len((rejected))+count_all
    print(count_all)
    print(add_count)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(results_dict,f,indent=2)
#statistics_bears(r"D:\NPR4J\Utils\Bears.json",r"D:\文档\icse2023\Bears补丁检查.xlsx",r"D:\文档\icse2023\bears_result.json")
def count_total_fixed(d4j_results_f):
    results=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
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

#count_total_fixed("D:\文档\icse2023\d4j_result.json")

def count_bug_types(results_sheet,output_f,sheet_name):
    bug_types={}
    results_all = pd.read_excel(results_sheet, sheet_name=sheet_name)
    for index,row in results_all.iterrows():
        Bug_Id=row["Bug-Id"]
        bug_type=row["Type"]
        buggy_line=row["Buggy-Line"]
        developer_line=row["Develop-Patch-Line"]
        bug_types[Bug_Id]={"buggy_line":buggy_line,"developer_line":developer_line,"BugType":bug_type}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(bug_types,f,indent=2)
#count_bug_types(r"D:\文档\icse2023\Defects4J补丁检查.xlsx",r"D:\文档\icse2023\d4j_bugtypes.json","Defects4J-Data")
#count_bug_types(r"D:\文档\icse2023\Bears补丁检查.xlsx",r"D:\文档\icse2023\bears_bugtypes.json","Bears-Data")
#count_bug_types(r"D:\文档\icse2023\QuixBugs补丁检查.xlsx",r"D:\文档\icse2023\qbs_bugtypes.json","QuixBugs-Data")

def analyze_bugtypes_fixed(d4j_results_f,bug_types):
    all_results=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
    bug_types=json.load(codecs.open(bug_types,'r',encoding='utf8'))
    bug_types_count={}
    fixed_sys_count={}
    def statistics_bug_types(list,bug_type_dict):
        results={}
        count_results={}
        for bug in list:
            bugtype=bug_type_dict[bug]["BugType"]
            if bugtype in results.keys():
                fixed_list=results[bugtype]
                fixed_list.append(bug)
                results[bugtype]=fixed_list
                count_results[bugtype]=len(fixed_list)
            else:
                results[bugtype] = [bug]
                count_results[bugtype] = 1
        return count_results
    for bug in all_results.keys():
        info=all_results[bug]
        ids = info["ids"]
        if len(ids)>1:
            pass
        else:
            id =ids[0]

            bug_type=bug_types[id]["BugType"]
            if bug_type not in bug_types_count.keys():
                bug_types_count[bug_type]=[bug]
            else:
                bug_list=bug_types_count[bug_type]
                bug_list.append(bug)
                bug_types_count[bug_type]=bug_list
            accepted_list=info["Accepted"]
            for hit in accepted_list:
                sys=hit["sys"]
                if sys in fixed_sys_count.keys():
                    fixed_list=fixed_sys_count[sys]
                    fixed_list.append(id)
                    fixed_sys_count[sys]=list(set(fixed_list))
                else:
                    fixed_sys_count[sys] = [id]

    for key in bug_types_count.keys():
        print(key,len(bug_types_count[key]))
    for sys in fixed_sys_count.keys():
        print(sys,statistics_bug_types(fixed_sys_count[sys],bug_types))
    pass
#analyze_bugtypes_fixed(r"D:\文档\icse2023\d4j_result.json",r"D:\文档\icse2023\d4j_bugtypes.json")