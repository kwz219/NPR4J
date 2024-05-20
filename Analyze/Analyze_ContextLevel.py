import codecs
import difflib
import json
import re

import javalang

from Analyze.Analyze_template import get_system_fixed_exclude, get_system_fixed_unexclude


def getContextLevel(id,src_tokens,tokens,input_dir):

    type_not=["inline"]
    pure_toks=[]
    for tok in tokens:
        if tok.isspace():
            continue
        pure_toks.append(tok)
    for token in tokens:
        if not token in src_tokens:
            type_not.append("notline")
            method=codecs.open(input_dir+'/buggy_methods/'+id+'.txt','r',encoding='utf8').read()
            if not token in method:
                type_not.append("notmethod")
                classcontent=codecs.open(input_dir+'/buggy_classes/'+id.split("_")[1]+'.java','r',encoding='utf8').read()
                if not token in classcontent:
                    type_not.append("notclass")
    if "notclass" in type_not:
        return "prj_outprj"
    elif "notmethod" in type_not:
        return "inclass"
    elif "notline" in type_not:
        return "inmethod"
    return "inline"


def draw_bugdiff_context(qbs_bugs_f,d4j_bugs_f,bears_bugs_f,input_dir,output_f):
    all_dict = {}
    qbs_bugs = json.load(codecs.open(qbs_bugs_f, 'r', encoding='utf8'))
    d4j_bugs = json.load(codecs.open(d4j_bugs_f, 'r', encoding='utf8'))
    bears_bugs = json.load(codecs.open(bears_bugs_f, 'r', encoding='utf8'))
    for bug in qbs_bugs.keys():
        origin_dict = qbs_bugs[bug]

        buggy_line = str(origin_dict["buggy_line"])
        developer_line = str(origin_dict["developer_line"])
        try:
            toked_buggy_line = javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line = javalang.tokenizer.tokenize(developer_line)

            toked_buggy = [tok.value for tok in toked_buggy_line]
            print(toked_buggy)
            toked_fix = [tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;(){}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;(){}=^+:|%<>*-])", buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy, toked_fix)

        diffs = []
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag == 'equal':
                diffs.append({"type": tag, "src": ''.join(toked_buggy[i1:i2]), "tgt": ''.join(toked_fix[j1:j2])})

        buggy_src = [item["src"].strip() for item in diffs]
        buggy_tgt = [item["tgt"].strip() for item in diffs]
        origin_dict["src"] = buggy_src
        origin_dict["tgt"] = buggy_tgt
        origin_dict["context_level"]=getContextLevel(bug,toked_buggy,buggy_tgt,input_dir)
        all_dict[bug] = origin_dict

    for bug in d4j_bugs.keys():
        origin_dict = d4j_bugs[bug]
        buggy_line = str(origin_dict["buggy_line"])
        developer_line = str(origin_dict["developer_line"])
        try:
            toked_buggy_line = javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line = javalang.tokenizer.tokenize(developer_line)
            toked_buggy = [tok.value for tok in toked_buggy_line]
            toked_fix = [tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;(){}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;(){}=^+:|%<>*-])", buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy, toked_fix)

        diffs = []
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag == 'equal':
                diffs.append({"type": tag, "src": ''.join(toked_buggy[i1:i2]), "tgt": ''.join(toked_fix[j1:j2])})
        buggy_src = [item["src"].strip() for item in diffs]
        buggy_tgt = [item["tgt"].strip() for item in diffs]
        origin_dict["src"] = buggy_src
        origin_dict["tgt"] = buggy_tgt
        origin_dict["context_level"]=getContextLevel(bug,toked_buggy,buggy_tgt,input_dir)
        all_dict[bug] = origin_dict

    for bug in bears_bugs.keys():
        origin_dict = bears_bugs[bug]
        buggy_line = str(origin_dict["buggy_line"])
        developer_line = str(origin_dict["developer_line"])
        try:
            toked_buggy_line = javalang.tokenizer.tokenize(buggy_line)
            toked_fix_line = javalang.tokenizer.tokenize(developer_line)
            toked_buggy = [tok.value for tok in toked_buggy_line]
            toked_fix = [tok.value for tok in toked_fix_line]
        except:
            toked_fix = re.split("([.,!?;(){}=^+:|%<>*-])", developer_line)
            toked_buggy = re.split("([.,!?;(){}=^+:|%<>*-])", buggy_line)
        matcher = difflib.SequenceMatcher(None, toked_buggy, toked_fix)

        diffs = []
        for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
            if not tag == 'equal':
                diffs.append({"type": tag, "src": ''.join(toked_buggy[i1:i2]), "tgt": ''.join(toked_fix[j1:j2])})
        buggy_src = [item["src"].strip() for item in diffs]
        buggy_tgt = [item["tgt"].strip() for item in diffs]
        origin_dict["src"] = buggy_src
        origin_dict["tgt"] = buggy_tgt
        origin_dict["context_level"]=getContextLevel(bug,toked_buggy,buggy_tgt,input_dir)
        all_dict[bug] = origin_dict

    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(all_dict, f, indent=2)

def analyze_uncovered(types_f,d4j_result_f,bears_result_f,qbs_result_f):
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
    types=json.load(codecs.open(types_f,'r',encoding='utf8'))
    all_exclude=FP_DR+FP_kw+FP_op+FP_NB+FP_Exp
    d4j_results=json.load(codecs.open(d4j_result_f,'r',encoding='utf8'))
    bears_results=json.load(codecs.open(bears_result_f,'r',encoding='utf8'))
    qbs_results=json.load(codecs.open(qbs_result_f,'r',encoding='utf8'))
    d4j_systems_fixed=get_system_fixed_unexclude(d4j_result_f,all_exclude)
    bears_systems_fixed = get_system_fixed_unexclude(bears_result_f, all_exclude)
    qbs_systems_fixed = get_system_fixed_unexclude(qbs_result_f, all_exclude)
    all_systems_fixed={}

    for sys in d4j_systems_fixed.keys():
        all_list=[]
        nonV=0
        inline=0
        inmethod=0
        inclass=0
        inproject=0
        outproject=0
        outprojectlist=[]
        if sys in d4j_systems_fixed.keys():
            all_list+=d4j_systems_fixed[sys]
        if sys in bears_systems_fixed.keys():
            all_list+=bears_systems_fixed[sys]
        if sys in qbs_systems_fixed.keys():
            all_list+=qbs_systems_fixed[sys]
        print(sys)
        for bug in all_list:
            bug=bug[0]
            if bug in d4j_results.keys():
                id = d4j_results[bug]["ids"][0]
            elif bug in bears_results.keys():
                id = bears_results[bug]["ids"][0]
            elif bug in qbs_results.keys():
                id =qbs_results[bug]["ids"][0]

            if  types[id]["BugType"]=="IncorrectOperator" or types[id]["context_level"]=="non_semantic":
                nonV+=1
            elif types[id]["context_level"]=="inline":
                inline+=1
            elif types[id]["context_level"] == "inmethod":
                inmethod += 1
            elif types[id]["context_level"] == "inclass":
                inclass += 1
            elif types[id]["context_level"] == "inproject":
                inproject += 1
            elif types[id]["context_level"] == "outproject":
                outproject += 1
                outprojectlist.append(id)
            else:
                print(id)
        print(nonV)
        print(inline)
        print(inmethod)
        print(inclass)
        print(inproject)
        print(outproject)
        print(outprojectlist)
        print('='*10)

def analyze_hand(ori_f,input_dir,output_f):
    checklist={}
    checklist["d4j_61a8cca68009e7c4a5d3d85a"]=["hasInstanceType"]
    checklist["d4j_61a8cca78009e7c4a5d3da0c"] = ["begin"]
    checklist["qbs_62381824123e2a7ca8437123"] = ["depth"]
    checklist["d4j_61a8cca58009e7c4a5d3d608"] = ["hasDecPoint"]
    checklist["d4j_61a8cca68009e7c4a5d3d6aa"] = ["method","hashCode"]
    checklist["d4j_61a8cca68009e7c4a5d3d757"] = ["typeParameter","actualTypeArgument"]
    checklist["d4j_61a8cca68009e7c4a5d3d78e"] = ["canCreateUsingArrayDelegate"]
    checklist["d4j_61a8cca68009e7c4a5d3d7a1"] = ["_hasSegments"]
    checklist["d4j_61a8cca78009e7c4a5d3d9d6"] = ["startIndex"]
    checklist["d4j_61a8cca78009e7c4a5d3d9f3"] = ["removeUnused"]
    checklist["bears_6257cdb15fef470c3d70c1b7"] = ["0xFF"]
    checklist["qbs_62381824123e2a7ca8437126"] = ["num_lessoreq"]
    checklist["qbs_62381824123e2a7ca8437140"] = ["lines","add","text"]
    checklist["d4j_61a8cca68009e7c4a5d3d947"] = ["_findTreeDeserializer"]
    checklist["d4j_61a8cca78009e7c4a5d3d9ca"] = ["mLocale"]
    checklist["d4j_61a8cca78009e7c4a5d3d9d2"] = ["body"]
    checklist["d4j_61a8cca68009e7c4a5d3d622"] = ["Math.max"]
    checklist["d4j_61a8cca68009e7c4a5d3d708"] = ["isNoType()"]
    checklist["d4j_61a8cca68009e7c4a5d3d78e"] = ["canCreateUsingArrayDelegate"]
    checklist["d4j_61a8cca68009e7c4a5d3d7e9"] = ["headerMap"]
    checklist["d4j_61a8cca68009e7c4a5d3d801"] = ["pos"]
    checklist["bears_6257cdb15fef470c3d70c275"] = ["parseInt","Integer"]
    checklist["d4j_61a8cca68009e7c4a5d3d6c9"] = ["children",".size()"]
    checklist["d4j_61a8cca68009e7c4a5d3d7a4"] = ["String.class"]
    checklist["qbs_62381824123e2a7ca8437131"] = ["coins","length"]
    checklist["bears_6257cdb05fef470c3d70c07f"] = ["exceptioninstanceofDeserializeException"]
    checklist["bears_6257cdb05fef470c3d70c0b1"] = ["_hasNullKey"]
    checklist["d4j_61a8cca68009e7c4a5d3d8e1"] = ["BIG_DECIMAL"]
    bug_context_types=json.load(codecs.open(ori_f,'r',encoding='utf8'))
    for id in checklist.keys():
        tokens=checklist[id]

        gtype=getContextLevel(id,str(bug_context_types[id]["buggy_line"]),tokens,input_dir)
        bug_context_types[id]["context_level"]=gtype
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(bug_context_types, f, indent=2)



