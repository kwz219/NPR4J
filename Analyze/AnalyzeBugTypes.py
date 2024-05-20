import codecs
import difflib
import json
import re

import javalang.tokenizer

from Analyze.Analyze_MRR import get_system_fixed

def count_bugTypes(d4j_types_f,bears_types_f,qbs_types_f,d4j_results_f,bears_results_f,qbs_results_f):
    d4j_types = json.load(codecs.open(d4j_types_f, 'r', encoding='utf8'))
    bears_types = json.load(codecs.open(bears_types_f, 'r', encoding='utf8'))
    qbs_types = json.load(codecs.open(qbs_types_f, 'r', encoding='utf8'))
    d4j_results=json.load(codecs.open(d4j_results_f,'r',encoding='utf8'))
    bears_results=json.load(codecs.open(bears_results_f,'r',encoding='utf8'))
    qbs_results=json.load(codecs.open(qbs_results_f,'r',encoding='utf8'))
    exclude_ids = []
    for bug in d4j_results.keys():
        ids=d4j_results[bug]["ids"]
        if len(ids)>1:
            exclude_ids+=ids
    for bug in bears_results.keys():
        ids=bears_results[bug]["ids"]

        if len(ids)>1:
            exclude_ids+=ids
    for bug in qbs_results.keys():
        ids=qbs_results[bug]["ids"]

        if len(ids)>1:
            exclude_ids+=ids
    all_types_count={}

    for id in d4j_types.keys():
        if id in exclude_ids:
            continue
        type=d4j_types[id]["BugType"]
        if type in all_types_count.keys():
            count=all_types_count[type]
            count+=1
            all_types_count[type]=count
        else:
            all_types_count[type]=1
    for id in bears_types.keys():
        if id in exclude_ids:
            continue
        type = bears_types[id]["BugType"]
        if type in all_types_count.keys():
            count=all_types_count[type]
            count+=1
            all_types_count[type]=count
        else:
            all_types_count[type]=1
    for id in qbs_types.keys():
        if id in exclude_ids:
            continue
        type = qbs_types[id]["BugType"]
        if type in all_types_count.keys():
            count=all_types_count[type]
            count+=1
            all_types_count[type]=count
        else:
            all_types_count[type]=1
    a = sorted(all_types_count.items(), key=lambda x: x[1], reverse=True)
    sum=0
    for key in a:
        print(key[0],key[1])
        sum+=key[1]
    print(sum)
def statistics_bug_types(list, bug_type_dict):
    results = {}
    count_results = {}

    for bug in list:
        #print(bug)
        bugtype = bug_type_dict[bug]["BugType"]
        if bugtype in results.keys():
            fixed_list = results[bugtype]
            fixed_list.append(bug)
            results[bugtype] = fixed_list
            count_results[bugtype] = len(fixed_list)
        else:
            results[bugtype] = [bug]
            count_results[bugtype] = 1
    return count_results

def analyze_bugTypes_fixed(types_dict,results_dict):
    all_results=json.load(codecs.open(results_dict,'r',encoding='utf8'))
    bug_types=json.load(codecs.open(types_dict,'r',encoding='utf8'))
    bug_types_count={}
    fixed_sys_count={}
    for bug in all_results.keys():
        info=all_results[bug]
        ids = info["ids"]
        if len(ids)>1:
            continue
        else:
            id =ids[0]
            if id not in bug_types.keys():
                continue
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

    return bug_types_count,fixed_sys_count

def get_fixed_certain_type(types_dict,results_dict,type="RedundantExpression"):
    sys_fixed_types={}
    all_results=json.load(codecs.open(results_dict,'r',encoding='utf8'))
    bug_types=json.load(codecs.open(types_dict,'r',encoding='utf8'))
    for bug in all_results.keys():
        info=all_results[bug]
        ids = info["ids"]
        if len(ids)>1:
            continue
        else:
            id =ids[0]
            if id not in bug_types.keys():
                continue
            bug_type=bug_types[id]["BugType"]
            if bug_type==type:
                accepted_list = info["Accepted"]
                for hit in accepted_list:
                    sys = hit["sys"]
                    if sys in sys_fixed_types.keys():
                        fixed_list = sys_fixed_types[sys]
                        fixed_list.append(id)
                        sys_fixed_types[sys] = list(set(fixed_list))
                    else:
                        sys_fixed_types[sys] = [id]
    return sys_fixed_types

    pass
def sum_fix_results(d4j_result,d4j_bugType,bears_result,bears_bugType,qbs_result,qbs_bugType):
        final_results={}
        for sys in d4j_result:
            fixed_list=d4j_result[sys]
            count_results_d4j=statistics_bug_types(fixed_list,d4j_bugType)
            count_results_bears=statistics_bug_types(bears_result[sys],bears_bugType)
            count_results_qbs=statistics_bug_types(qbs_result[sys],qbs_bugType)
            for type in count_results_bears.keys():
                fixed_count=count_results_bears[type]
                if type in count_results_d4j.keys():
                    old_fixed=count_results_d4j[type]
                    new_fixed=old_fixed+fixed_count
                    count_results_d4j[type]=new_fixed
                else:
                    count_results_d4j[type]=fixed_count
            for type in count_results_qbs.keys():
                fixed_count=count_results_qbs[type]
                if type in count_results_d4j.keys():
                    old_fixed=count_results_d4j[type]
                    new_fixed=old_fixed+fixed_count
                    count_results_d4j[type]=new_fixed
                else:
                    count_results_d4j[type]=fixed_count
            final_results[sys]=count_results_d4j
        return final_results
def count_all(d4j_types_dict,d4j_results_dict,bears_types_dict,bears_results_dict,qbs_types_dict,qbs_results_dict):
    d4j_bugTypes,d4j_results=analyze_bugTypes_fixed(d4j_types_dict,d4j_results_dict)
    bears_bugTypes,bears_results=analyze_bugTypes_fixed(bears_types_dict,bears_results_dict)
    qbs_bugTypes,qbs_results=analyze_bugTypes_fixed(qbs_types_dict,qbs_results_dict)
    all_bugTypes={}

    for bugtype in d4j_bugTypes.keys():
        all_bugTypes[bugtype]=d4j_bugTypes[bugtype]
    for bugtype in bears_bugTypes.keys():
        if bugtype in all_bugTypes.keys():
            new_count=all_bugTypes[bugtype]+bears_bugTypes[bugtype]
            all_bugTypes[bugtype]=new_count
        else:
            all_bugTypes[bugtype]=bears_bugTypes[bugtype]
    for bugtype in qbs_bugTypes.keys():
        if bugtype in all_bugTypes.keys():
            new_count=all_bugTypes[bugtype]+qbs_bugTypes[bugtype]
            all_bugTypes[bugtype]=new_count
        else:
            all_bugTypes[bugtype]=qbs_bugTypes[bugtype]
    a = sorted(all_bugTypes.items(), key=lambda x: len(x[1]), reverse=True)

    systems_fixed=sum_fix_results(d4j_results,json.load(codecs.open(d4j_types_dict,'r',encoding='utf8')),
                                  bears_results,json.load(codecs.open(bears_types_dict,'r',encoding='utf8')),
                                  qbs_results,json.load(codecs.open(qbs_types_dict,'r',encoding='utf8')))

    for key in systems_fixed.keys():
        print(key,systems_fixed[key])

def find_fixed_longlogic(d4j_types_dict,d4j_results_dict_f,bears_types_dict,bears_results_dict_f,qbs_types_dict,qbs_results_dict_f):
    MissingLongLogic=[]
    d4j_types=json.load(codecs.open(d4j_types_dict,'r',encoding='utf8'))
    bears_types=json.load(codecs.open(bears_types_dict,'r',encoding='utf8'))
    qbs_types=json.load(codecs.open(qbs_types_dict,'r',encoding='utf8'))
    d4j_results_dict=json.load(codecs.open(d4j_results_dict_f,'r',encoding='utf8'))
    bears_results_dict=json.load(codecs.open(bears_results_dict_f,'r',encoding='utf8'))
    qbs_results_dict=json.load(codecs.open(qbs_results_dict_f,'r',encoding='utf8'))
    for id in d4j_types.keys():
        if d4j_types[id]["BugType"]=="MissingBooleanExpression":
            MissingLongLogic.append(id)
    for id in bears_types.keys():
        if bears_types[id]["BugType"]=="IncorrectWholeExpressionOrStatement":
            MissingLongLogic.append(id)
    for id in qbs_types.keys():
        if qbs_types[id]["BugType"]=="IncorrectWholeExpressionOrStatement":
            MissingLongLogic.append(id)
    for bug in d4j_results_dict.keys():
        ids =d4j_results_dict[bug]["ids"]
        if len(ids)==1:
            if ids[0] in MissingLongLogic:
                print(bug,d4j_results_dict[bug]["Accepted"])
    for bug in bears_results_dict.keys():
        ids =bears_results_dict[bug]["ids"]
        if len(ids)==1:
            if ids[0] in MissingLongLogic:
                print(bug,bears_results_dict[bug]["Accepted"])
    for bug in qbs_results_dict.keys():
        ids =qbs_results_dict[bug]["ids"]
        if len(ids)==1:
            if ids[0] in MissingLongLogic:
                print(bug,qbs_results_dict[bug]["Accepted"])

def find_most_fixed_bugs(d4j_results_dict_f,bears_results_dict_f,qbs_results_dict_f):
    d4j_results_dict=json.load(codecs.open(d4j_results_dict_f,'r',encoding='utf8'))
    bears_results_dict=json.load(codecs.open(bears_results_dict_f,'r',encoding='utf8'))
    qbs_results_dict=json.load(codecs.open(qbs_results_dict_f,'r',encoding='utf8'))
    bug_systems={}
    for bug in d4j_results_dict.keys():
        bug_info=d4j_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    for bug in bears_results_dict.keys():
        bug_info=bears_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    for bug in qbs_results_dict.keys():
        bug_info=qbs_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    a = sorted(bug_systems.items(), key=lambda x: len(x[1]), reverse=True)
    for k in a:
        print(k[0],len(k[1]),k[1])
def find_single_fixed_bugs(d4j_results_dict_f,bears_results_dict_f,qbs_results_dict_f):
    d4j_results_dict=json.load(codecs.open(d4j_results_dict_f,'r',encoding='utf8'))
    bears_results_dict=json.load(codecs.open(bears_results_dict_f,'r',encoding='utf8'))
    qbs_results_dict=json.load(codecs.open(qbs_results_dict_f,'r',encoding='utf8'))
    bug_systems={}
    for bug in d4j_results_dict.keys():
        bug_info=d4j_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    for bug in bears_results_dict.keys():
        bug_info=bears_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    for bug in qbs_results_dict.keys():
        bug_info=qbs_results_dict[bug]
        ids=bug_info["ids"]
        if len(ids)==1:
            systems=set()
            accepted=bug_info["Accepted"]
            for re in accepted:
                systems.add(re["sys"])
            bug_systems[bug]=list(systems)
    a = sorted(bug_systems.items(), key=lambda x: len(x[1]), reverse=True)
    systems_single_fixed={}
    for k in a:
        bug=k[0]
        fix_list=k[1]
        if len(fix_list)==1:
            sys =fix_list[0]
            if sys in systems_single_fixed.keys():
                bugs=systems_single_fixed[sys]
                bugs.append(bug)
                systems_single_fixed[sys]=bugs
            else:
                systems_single_fixed[sys]=[bug]
    for key in systems_single_fixed.keys():
        print(key,len(systems_single_fixed[key]),systems_single_fixed[key])
def print_fixed_forflower(d4j_results_f,bears_results_f,qbs_results_f):
    systems_d4j=get_system_fixed(d4j_results_f)
    systems_bears=get_system_fixed(bears_results_f)
    systems_qbs=get_system_fixed(qbs_results_f)
    print("Bug"+'\t'+"System")
    for key in systems_d4j.keys():
        fixed_list=systems_d4j[key]
        for item in fixed_list:
            print(str(item[0])+'\t'+key)
    for key in systems_bears.keys():
        fixed_list=systems_bears[key]
        for item in fixed_list:
            print(str(item[0])+'\t'+key)
    for key in systems_qbs.keys():
        fixed_list=systems_qbs[key]
        for item in fixed_list:
            print(str(item[0])+'\t'+key)
    pass

def print_fixed_forupset(d4j_results_f,bears_results_f,qbs_results_f):
    systems_d4j=get_system_fixed(d4j_results_f)
    systems_bears=get_system_fixed(bears_results_f)
    systems_qbs=get_system_fixed(qbs_results_f)
    systems_all={}


    for sys in systems_d4j.keys():
        fixed_list=systems_d4j[sys]
        systems_all[sys]=fixed_list+systems_bears[sys]+systems_qbs[sys]

    for sys in systems_all.keys():
        print(sys)
        for item in systems_all[sys]:
            print(item[0])
        print("=="*10)
def draw_bug_diffs(qbs_bugs_f,d4j_bugs_f,bears_bugs_f,output_f):
    all_dict={}
    qbs_bugs=json.load(codecs.open(qbs_bugs_f,'r',encoding='utf8'))
    d4j_bugs=json.load(codecs.open(d4j_bugs_f,'r',encoding='utf8'))
    bears_bugs=json.load(codecs.open(bears_bugs_f,'r',encoding='utf8'))
    for bug in qbs_bugs.keys():
        origin_dict=qbs_bugs[bug]

        buggy_line=str(origin_dict["buggy_line"])
        developer_line=str(origin_dict["developer_line"])
        try:
            toked_buggy_line=javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line=javalang.tokenizer.tokenize(developer_line)

            toked_buggy=[tok.value for tok in toked_buggy_line]
            print(toked_buggy)
            toked_fix=[tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;(){}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;(){}=^+:|%<>*-])",buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy,toked_fix)
        buggy_src=""
        buggy_tgt=""
        diffs=[]
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag=='equal':
                diffs.append({"type":tag,"src":''.join(toked_buggy[i1:i2]),"tgt":''.join(toked_fix[j1:j2])})
        if len(diffs)==1:
            buggy_src=diffs[0]["src"].strip()
            buggy_tgt=diffs[0]["tgt"].strip()
        origin_dict["src"]=buggy_src
        origin_dict["tgt"]=buggy_tgt
        all_dict[bug]=origin_dict

    for bug in d4j_bugs.keys():
        origin_dict=d4j_bugs[bug]
        buggy_line=str(origin_dict["buggy_line"])
        developer_line=str(origin_dict["developer_line"])
        try:
            toked_buggy_line=javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line=javalang.tokenizer.tokenize(developer_line)
            toked_buggy=[tok.value for tok in toked_buggy_line]
            toked_fix=[tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;()&{}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;()&{}=^+:|%<>*-])",buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy,toked_fix)
        buggy_src=""
        buggy_tgt=""
        diffs=[]
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag=='equal':
                diffs.append({"type":tag,"src":''.join(toked_buggy[i1:i2]),"tgt":''.join(toked_fix[j1:j2])})
        if len(diffs)==1:
            buggy_src=diffs[0]["src"].strip()
            buggy_tgt=diffs[0]["tgt"].strip()
        origin_dict["src"]=buggy_src
        origin_dict["tgt"]=buggy_tgt
        all_dict[bug]=origin_dict

    for bug in bears_bugs.keys():
        origin_dict=bears_bugs[bug]
        buggy_line=str(origin_dict["buggy_line"])
        developer_line=str(origin_dict["developer_line"])
        try:
            toked_buggy_line=javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line=javalang.tokenizer.tokenize(developer_line)
            toked_buggy=[tok.value for tok in toked_buggy_line]
            toked_fix=[tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;(){}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;(){}=^+:|%<>*-])",buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy,toked_fix)
        buggy_src=""
        buggy_tgt=""
        diffs=[]
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag=='equal':
                diffs.append({"type":tag,"src":''.join(toked_buggy[i1:i2]),"tgt":''.join(toked_fix[j1:j2])})
        if len(diffs)==1:
            buggy_src=diffs[0]["src"].strip()
            buggy_tgt=diffs[0]["tgt"].strip()
        origin_dict["src"]=buggy_src
        origin_dict["tgt"]=buggy_tgt
        all_dict[bug]=origin_dict

    with open(output_f,'w',encoding='utf8')as f:
        json.dump(all_dict,f,indent=2)

def count_bugtypes_data_level(d4j_types_dict,d4j_results_dict,bears_types_dict,bears_results_dict,qbs_types_dict,qbs_results_dict,output_f):
    d4j_bugTypes,d4j_results=analyze_bugTypes_fixed(d4j_types_dict,d4j_results_dict)
    bears_bugTypes,bears_results=analyze_bugTypes_fixed(bears_types_dict,bears_results_dict)
    qbs_bugTypes,qbs_results=analyze_bugTypes_fixed(qbs_types_dict,qbs_results_dict)
    systems_fixed=sum_fix_results(d4j_results,json.load(codecs.open(d4j_types_dict,'r',encoding='utf8')),
                                  bears_results,json.load(codecs.open(bears_types_dict,'r',encoding='utf8')),
                                  qbs_results,json.load(codecs.open(qbs_types_dict,'r',encoding='utf8')))
    token_level=["IncorrectVariable","IncorrectFunctionCall","IncorrectOperator","MissingVariable","IncorrectNumberValue",
                "IncorrectKeyword","MissingFunctionCallOrConstructor" ]
    tok_level_id=["d4j_61a8cca68009e7c4a5d3d8c0","d4j_61a8cca78009e7c4a5d3d9fe","d4j_61a8cca78009e7c4a5d3d9ff","d4j_61a8cca78009e7c4a5d3da00",
                  "d4j_61a8cca78009e7c4a5d3da01","d4j_61a8cca78009e7c4a5d3da02","d4j_61a8cca78009e7c4a5d3da03","d4j_61a8cca78009e7c4a5d3da04",
                  "d4j_61a8cca78009e7c4a5d3da05","d4j_61a8cca68009e7c4a5d3d826","d4j_61a8cca68009e7c4a5d3d827","d4j_61a8cca68009e7c4a5d3d828",
                  "d4j_61a8cca68009e7c4a5d3d829","bears_6257cdb05fef470c3d70c051","bears_6257cdb15fef470c3d70c198","bears_6257cdb15fef470c3d70c113",
                  "bears_6257cdb15fef470c3d70c11a","bears_6257cdb15fef470c3d70c13d","bears_6257cdb15fef470c3d70c13e","bears_6257cdb15fef470c3d70c16d",
                  "bears_6257cdb15fef470c3d70c170","bears_6257cdb15fef470c3d70c171","bears_6257cdb15fef470c3d70c172","bears_6257cdb15fef470c3d70c229","bears_6257cdb15fef470c3d70c21d",
                  ]
    pstmt_level_id=["d4j_61a8cca68009e7c4a5d3d910","d4j_61a8cca58009e7c4a5d3d5fe","d4j_61a8cca58009e7c4a5d3d600","d4j_61a8cca68009e7c4a5d3d923",
                    "d4j_61a8cca68009e7c4a5d3d924","d4j_61a8cca68009e7c4a5d3d8a9","d4j_61a8cca68009e7c4a5d3d84d","bears_6257cdb15fef470c3d70c257",
                   "bears_6257cdb15fef470c3d70c261","bears_6257cdb15fef470c3d70c1bc","bears_6257cdb05fef470c3d70c061","bears_6257cdb05fef470c3d70c062",
                    "bears_6257cdb15fef470c3d70c119", "bears_6257cdb15fef470c3d70c13c",
                    "bears_6257cdb05fef470c3d70c064","bears_6257cdb05fef470c3d70c0bd","bears_6257cdb15fef470c3d70c2ad"]
    whole_level_id=["d4j_61a8cca68009e7c4a5d3d795","d4j_61a8cca68009e7c4a5d3d80d","d4j_61a8cca78009e7c4a5d3d960",
                    "d4j_61a8cca68009e7c4a5d3d663","bears_6257cdb15fef470c3d70c1c1"]
    partial_level=["IncorrectPartialExpressionOrStatement","MissingPartialStatementOrExpression","ExpressionSwap"]
    whole_level=["MissingBooleanExpression","MissingNullCheck","IncorrectWholeExpressionOrStatement","MissingWholeExpressionOrStatement","IncorrectBooleanExpression"]
    multi_level=["MissingLongLogic","MissingMultipleBooleanExpression","MissingException","IncorrectLongLogic"]
    red_lv=["RedundantExpression"]
    sys_level={}
    all_lines=[",".join(["","token-level","partialStmt-level","wholeStmt-level","multiStmt-level"])]
    systems = ["Edits", "Tufano", "CoCoNut", "CodeBERT-ft", "RewardRepair", "Recoder", "SequenceR", "Recoder_ori",
               "RewardRepair_ori"]
    d4j_fixed=get_fixed_certain_type(d4j_types_dict,d4j_results_dict,type="RedundantExpression")
    bears_fixed=get_fixed_certain_type(bears_types_dict,bears_results_dict,type="RedundantExpression")
    qbs_fixed=get_fixed_certain_type(qbs_types_dict,qbs_results_dict,type="RedundantExpression")

    token_dict=set()
    partialStmt_dict=set()
    wholeStmt_dict=set()
    multiStmt_dict=set()
    for sys in systems:
        token_count=0
        partial_count=0
        whole_count=0
        multi_count=0
        red_count=0
        results=systems_fixed[sys]
        type_ids=[]
        if sys in d4j_fixed.keys():
            type_ids+=d4j_fixed[sys]
        if sys in bears_fixed.keys():
            type_ids+=bears_fixed[sys]
        if sys in qbs_fixed.keys():
            type_ids+=qbs_fixed[sys]

        for type in results.keys():
            count=results[type]
            if type in token_level:
                #token_dict.add(id)
                token_count+=count
            elif type in partial_level:
                partial_count+=count
                #partialStmt_dict.add(id)
            elif type in whole_level:
                whole_count+=count
                #wholeStmt_dict.add(id)
            elif type in multi_level:
                multi_count+=count
                #wholeStmt_dict.add(id)

        for id in type_ids:
            if id in tok_level_id:
                token_count+=1
                token_dict.add(id)
            elif id in pstmt_level_id:
                partial_count+=1
                partialStmt_dict.add(id)
            elif id in whole_level_id:
                whole_count+=1
                wholeStmt_dict.add(id)
            else:
                print(id)
                red_count+=1

        all_lines.append(','.join([sys,str(token_count),str(partial_count),str(whole_count),str(multi_count),str(red_count)]))
    """
    with open(output_f,'w',encoding='utf8')as f:
        for line in all_lines:
            f.write(line+'\n')
        f.close()
    """
    print(len(token_dict),len(partialStmt_dict),len(wholeStmt_dict))
    pass

def count_bugtypes_state(d4j_types_dict,d4j_results_dict,bears_types_dict,bears_results_dict,qbs_types_dict,qbs_results_dict,output_f):

    d4j_bugTypes,d4j_results=analyze_bugTypes_fixed(d4j_types_dict,d4j_results_dict)
    bears_bugTypes,bears_results=analyze_bugTypes_fixed(bears_types_dict,bears_results_dict)
    qbs_bugTypes,qbs_results=analyze_bugTypes_fixed(qbs_types_dict,qbs_results_dict)
    systems_fixed=sum_fix_results(d4j_results,json.load(codecs.open(d4j_types_dict,'r',encoding='utf8')),
                                  bears_results,json.load(codecs.open(bears_types_dict,'r',encoding='utf8')),
                                  qbs_results,json.load(codecs.open(qbs_types_dict,'r',encoding='utf8')))
    Incorrect=["IncorrectVariable","IncorrectFunctionCall","IncorrectOperator","IncorrectNumberValue","IncorrectKeyword",
               "IncorrectPartialExpressionOrStatement","IncorrectLongLogic","IncorrectBooleanExpression","ExpressionSwap","IncorrectWholeExpressionOrStatement"]
    Missing=["MissingVariable","MissingFunctionCallOrConstructor","MissingBooleanExpression","MissingNullCheck","MissingWholeExpressionOrStatement",
             "MissingLongLogic","MissingMultipleBooleanExpression","MissingException","MissingPartialStatementOrExpression"]
    Redundant=["RedundantExpression"]

    all_lines=[",".join(["","Incorrect","Missing","Redundant"])]
    systems = ["Edits", "Tufano", "CoCoNut", "CodeBERT-ft", "RewardRepair", "Recoder", "SequenceR", "Recoder_ori",
               "RewardRepair_ori"]
    for sys in systems:
        incorrect_count=0
        missing_count=0
        redundant_count=0
        results=systems_fixed[sys]



        for type in results.keys():
            count=results[type]
            if type in Incorrect:
                incorrect_count+=count
            elif type in Missing:
                missing_count+=count
            elif type in Redundant:
                redundant_count+=count
            else:
                print(type)

        all_lines.append(','.join([sys,str(incorrect_count),str(missing_count),str(redundant_count)]))
    with open(output_f,'w',encoding='utf8')as f:
        for line in all_lines:
            f.write(line+'\n')
        f.close()
    pass

def count_composition(d4j_types_dict,d4j_results_dict,bears_types_dict,bears_results_dict,qbs_types_dict,qbs_results_dict):
    d4j_bugTypes,d4j_results=analyze_bugTypes_fixed(d4j_types_dict,d4j_results_dict)
    bears_bugTypes,bears_results=analyze_bugTypes_fixed(bears_types_dict,bears_results_dict)
    qbs_bugTypes,qbs_results=analyze_bugTypes_fixed(qbs_types_dict,qbs_results_dict)
    print("d4j")
    for key in d4j_bugTypes.keys():
        print(key,len(d4j_bugTypes[key]))
    print('='*100)
    for key in bears_bugTypes.keys():
        print(key, len(bears_bugTypes[key]))
    print('='*100)
    for key in qbs_bugTypes.keys():
        print(key, len(qbs_bugTypes[key]))
    print('-----')
    all_sum=0
    for key in d4j_bugTypes.keys():
        sum=len(d4j_bugTypes[key])
        if key in qbs_bugTypes.keys():
            sum=sum+len(qbs_bugTypes[key])
        if key in bears_bugTypes.keys():
            sum+=len(bears_bugTypes[key])
        all_sum+=sum
        print(key,sum)
    print(all_sum)
def write_one_line_ids(d4j_result_f,bears_result_f,qbs_result_f,output_f):
    d4j_result=json.load(codecs.open(d4j_result_f,'r',encoding='utf8'))
    bears_result=json.load(codecs.open(bears_result_f,'r',encoding='utf8'))
    qbs_result=json.load(codecs.open(qbs_result_f,'r',encoding='utf8'))
    one_line_bugs=[]
    for bug in d4j_result.keys():
        ids=d4j_result[bug]["ids"]
        if len(ids)==1:
            one_line_bugs.append(ids[0])
    for bug in bears_result.keys():
        ids=bears_result[bug]["ids"]
        if len(ids)==1:
            one_line_bugs.append(ids[0])
    for bug in qbs_result.keys():
        ids=qbs_result[bug]["ids"]
        if len(ids)==1:
            one_line_bugs.append(ids[0])
    with open(output_f,'w',encoding='utf8')as f:
        for id in one_line_bugs:
            f.write(id+'\n')
#write_one_line_ids(r"D:\文档\icse2023\d4j_result_2.json",r"D:\文档\icse2023\bears_result.json",r"D:\文档\icse2023\qbs_result.json",r"D:\文档\icse2023\oneline_ids2.txt")
def count_composition_edit_scope(all_dict_f,oneline_ids_f):
    all_types=json.load(codecs.open(all_dict_f,'r',encoding='utf8'))
    oneline_ids=[]
    with open(oneline_ids_f,'r',encoding='utf8')as f:
        for line in f:
            oneline_ids.append(line.strip())
        f.close()
    token_level = ["IncorrectVariable", "IncorrectFunctionCall", "IncorrectOperator", "MissingVariable",
                   "IncorrectNumberValue",
                   "IncorrectKeyword", "MissingFunctionCallOrConstructor"]
    tok_level_id = ["d4j_61a8cca68009e7c4a5d3d8c0", "d4j_61a8cca78009e7c4a5d3d9fe", "d4j_61a8cca78009e7c4a5d3d9ff",
                    "d4j_61a8cca78009e7c4a5d3da00",
                    "d4j_61a8cca78009e7c4a5d3da01", "d4j_61a8cca78009e7c4a5d3da02", "d4j_61a8cca78009e7c4a5d3da03",
                    "d4j_61a8cca78009e7c4a5d3da04",
                    "d4j_61a8cca78009e7c4a5d3da05", "d4j_61a8cca68009e7c4a5d3d826", "d4j_61a8cca68009e7c4a5d3d827",
                    "d4j_61a8cca68009e7c4a5d3d828",
                    "d4j_61a8cca68009e7c4a5d3d829", "bears_6257cdb05fef470c3d70c051", "bears_6257cdb15fef470c3d70c198",
                    "bears_6257cdb15fef470c3d70c113",
                    "bears_6257cdb15fef470c3d70c11a", "bears_6257cdb15fef470c3d70c13d",
                    "bears_6257cdb15fef470c3d70c13e", "bears_6257cdb15fef470c3d70c16d",
                    "bears_6257cdb15fef470c3d70c170", "bears_6257cdb15fef470c3d70c171",
                    "bears_6257cdb15fef470c3d70c172", "bears_6257cdb15fef470c3d70c229",
                    "bears_6257cdb15fef470c3d70c21d",
                    ]
    pstmt_level_id = ["d4j_61a8cca68009e7c4a5d3d910", "d4j_61a8cca58009e7c4a5d3d5fe", "d4j_61a8cca58009e7c4a5d3d600",
                      "d4j_61a8cca68009e7c4a5d3d923",
                      "d4j_61a8cca68009e7c4a5d3d924", "d4j_61a8cca68009e7c4a5d3d8a9", "d4j_61a8cca68009e7c4a5d3d84d",
                      "bears_6257cdb15fef470c3d70c257",
                      "bears_6257cdb15fef470c3d70c261", "bears_6257cdb15fef470c3d70c1bc",
                      "bears_6257cdb05fef470c3d70c061", "bears_6257cdb05fef470c3d70c062",
                      "bears_6257cdb15fef470c3d70c119", "bears_6257cdb15fef470c3d70c13c",
                      "bears_6257cdb05fef470c3d70c064", "bears_6257cdb05fef470c3d70c0bd",
                      "bears_6257cdb15fef470c3d70c2ad"]
    whole_level_id = ["d4j_61a8cca68009e7c4a5d3d795", "d4j_61a8cca68009e7c4a5d3d80d", "d4j_61a8cca78009e7c4a5d3d960",
                      "d4j_61a8cca68009e7c4a5d3d663", "bears_6257cdb15fef470c3d70c1c1"]
    partial_level = ["IncorrectPartialExpressionOrStatement", "MissingPartialStatementOrExpression", "ExpressionSwap"]
    whole_level = ["MissingBooleanExpression", "MissingNullCheck", "IncorrectWholeExpressionOrStatement",
                   "MissingWholeExpressionOrStatement", "IncorrectBooleanExpression"]
    multi_level = ["MissingLongLogic", "MissingMultipleBooleanExpression", "MissingException", "IncorrectLongLogic","MissingMultipleBoolean"]

    token_count=0
    partial_count=0
    whole_count=0
    multi_count=0

    for id in all_types.keys():
        if id not in oneline_ids:
            continue
        info=all_types[id]
        type=info["BugType"]
        if type in token_level:
            token_count+=1
        elif type in partial_level:
            partial_count+=1
        elif type in whole_level:
            whole_count+=1
        elif type in  multi_level:
            multi_count+=1
        elif type == "RedundantExpression":
            if id in tok_level_id:
                token_count+=1
            elif id in pstmt_level_id:
                partial_count+=1
            elif id in whole_level_id:
                whole_count+=1
            else:
                print(id)
        else:
            print(id)
    print(token_count)
    print(partial_count)
    print(whole_count)
    print(multi_count)
#count_composition_edit_scope(r"D:\文档\icse2023\bugs_contextType2.json",r"D:\文档\icse2023\oneline_ids.txt")
def count_composition_state(all_dict_f,oneline_ids_f):
    all_types=json.load(codecs.open(all_dict_f,'r',encoding='utf8'))
    oneline_ids=[]
    with open(oneline_ids_f,'r',encoding='utf8')as f:
        for line in f:
            oneline_ids.append(line.strip())
        f.close()
    Incorrect=["IncorrectVariable","IncorrectFunctionCall","IncorrectOperator","IncorrectNumberValue","IncorrectKeyword",
               "IncorrectPartialExpressionOrStatement","IncorrectLongLogic","IncorrectBooleanExpression","ExpressionSwap","IncorrectWholeExpressionOrStatement"]
    Missing=["MissingVariable","MissingFunctionCallOrConstructor","MissingBooleanExpression","MissingNullCheck","MissingWholeExpressionOrStatement",
             "MissingLongLogic","MissingMultipleBooleanExpression","MissingException","MissingPartialStatementOrExpression","MissingMultipleBoolean"]
    Redundant=["RedundantExpression"]
    incorrect_count=0
    missing_count=0
    redundant_count=0

    for id in all_types.keys():
        if id not in oneline_ids:
            continue
        info=all_types[id]
        type=info["BugType"]
        if type in Incorrect:
            incorrect_count+=1
        elif type in Missing:
            missing_count+=1
        elif type in Redundant:
            redundant_count+=1

        else:
            print(id)
    print(incorrect_count)
    print(missing_count)
    print(redundant_count)
#count_composition_state(r"D:\文档\icse2023\bugs_contextType.json",r"D:\文档\icse2023\oneline_ids2.txt")