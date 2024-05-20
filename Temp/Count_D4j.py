import codecs
import json


def count_correct_plausible(identical_json,plausible_json,correct_json):
    correct_dict={"Chart":[],"Cli":[],"Closure":[],"Codec":[],"Collections":[],"Compress":[],
                  "Csv":[],"Gson":[],"JacksonCore":[],"JacksonDatabind":[],"JacksonXml":[],
                  "Jsoup":[],"JxPath":[],"Lang":[],"Math":[],"Mockito":[],"Time":[]}
    plausible_dict={"Chart":[],"Cli":[],"Closure":[],"Codec":[],"Collections":[],"Compress":[],
                  "Csv":[],"Gson":[],"JacksonCore":[],"JacksonDatabind":[],"JacksonXml":[],
                  "Jsoup":[],"JxPath":[],"Lang":[],"Math":[],"Mockito":[],"Time":[]}

    identical_result=json.load(codecs.open(identical_json,'r',encoding='utf8'))
    plausible_result=json.load(codecs.open(plausible_json,'r',encoding='utf8'))
    correct_result=json.load(codecs.open(correct_json,'r',encoding='utf8'))
    for bug in identical_result.keys():
        hit_tools=identical_result[bug]
        project=bug.split("_")[0]
        for tool in hit_tools:
            if "CoCoNut" in tool:
                old_set=correct_dict[project]
                old_set.append(bug)
                correct_dict[project]=old_set
                set2=plausible_dict[project]
                set2.append(bug)
                plausible_dict[project]=set2
                break
    for bug in correct_result.keys():
        hit_tools=correct_result[bug]
        project=bug.split("_")[0]
        for tool in hit_tools:
            if "CoCoNut" in tool:
                old_set=correct_dict[project]
                old_set.append(bug)
                correct_dict[project]=old_set
                break
    for bug in plausible_result.keys():
        hit_tools=plausible_result[bug]
        project=bug.split("_")[0]
        for tool in hit_tools:
            if "CoCoNut" in tool:
                set2=plausible_dict[project]
                set2.append(bug)
                plausible_dict[project]=set2
                break

    for project in correct_dict.keys():
        print(project,len(set(correct_dict[project])))

    print("============================")
    for project in plausible_dict.keys():
        print(project,len(set(plausible_dict[project])))

    for key in correct_dict.keys():
        #print(key)
        fix_list=correct_dict[key]
        fix_set=list(set(fix_list))
        correct_dict[key]=fix_set
    for key in plausible_dict.keys():
        fix_list=plausible_dict[key]
        fix_set=list(set(fix_list))
        plausible_dict[key]=fix_set
    with open("correct_CoCoNut.json",'w',encoding='utf8')as f:
        json.dump(correct_dict,f,indent=2)

    with open("plausible_CoCoNut.json",'w',encoding='utf8')as f:
        json.dump(plausible_dict,f,indent=2)

count_correct_plausible(r"E:\NPR4J\Eval_result\d4j\d4j_identical.json",r"E:\NPR4J\Eval_result\d4j\d4j_plausible.json",r"E:\NPR4J\Eval_result\d4j\d4j_correct.json")