import codecs
import json

import pandas
from Utils.IOHelper import readF2L
import xlsxwriter
def readF2L_nostrip(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line)
        f.close()
    return lines

def prepare_d4j(infos_f,input_dir):
    infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))
    d4j_infos=infos["d4j"]
    bug_names=[]
    bug_ids=[]
    buggy_methods=[]
    buggy_lines=[]
    develop_patch_lines=[]
    for bugName in d4j_infos.keys():
        bug_infos=d4j_infos[bugName]
        current_bug_names = []
        current_bug_ids = []
        current_buggy_methods = []
        current_buggy_lines = []
        current_develop_patch_lines = []
        for changeFile in bug_infos.keys():
            ids=bug_infos[changeFile]["ids"]
            for id in ids:
                id="d4j_"+id
                buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + '.txt', 'r', encoding='utf8').read().strip()
                develop_patch_line = codecs.open(input_dir + '/fix_lines/' + id + '.txt', 'r',
                                                 encoding='utf8').read().strip()
                meta_infos = codecs.open(input_dir + '/metas/' + id + '.txt', 'r',
                                         encoding='utf8').read().strip().split(
                    "<sep>")
                buggy_method = readF2L_nostrip(input_dir + '/buggy_methods/' + id + '.txt')
                buggy_line_id = int(meta_infos[2].split(":")[0][1:])
                buggy_method[buggy_line_id] = "<START_BUG> " + buggy_method[buggy_line_id].strip() + " <END_BUG>" + '\n'
                clean_method = []
                for line in buggy_method:
                    if len(line.strip()) == 0:
                        continue
                    clean_method.append(line)
                current_bug_names.append(bugName)
                current_bug_ids.append(id)
                current_buggy_methods.append(''.join(clean_method))
                current_buggy_lines.append(buggy_line)
                current_develop_patch_lines.append(develop_patch_line)
        bug_names=bug_names+current_bug_names
        bug_ids=bug_ids+current_bug_ids
        buggy_methods=buggy_methods+current_buggy_methods
        buggy_lines=buggy_lines+current_buggy_lines
        develop_patch_lines=develop_patch_lines+current_develop_patch_lines
    data_frame=pandas.DataFrame({"Bug-name":bug_names,"Bug-Id":bug_ids,"Buggy-Method":buggy_methods,"Buggy-Line":buggy_lines,
                                 "Develop-Patch-Line":develop_patch_lines})
    data_frame.to_excel("d4j_data.xlsx",engine="xlsxwriter")
#prepare_d4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json","E:/NPR4J/RawData (2)/Benchmarks")

def prepare_Bears(infos_f,input_dir):
    infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))
    bug_names=[]
    bug_ids=[]
    buggy_methods=[]
    buggy_lines=[]
    develop_patch_lines=[]
    for bug in infos.keys():
        Bug_infos=infos[bug]
        current_bug_names = []
        current_bug_ids = []
        current_buggy_methods = []
        current_buggy_lines = []
        current_develop_patch_lines = []
        for id in Bug_infos.keys():
            buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt','r',encoding='utf8').read().strip()
            develop_patch_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt','r',encoding='utf8').read().strip()
            meta_infos = codecs.open(input_dir + '/metas/' + id + '.txt', 'r', encoding='utf8').read().strip().split(
                "<sep>")
            buggy_method = readF2L_nostrip(input_dir + '/buggy_methods/' + id + '.txt')
            buggy_line_id = int(meta_infos[2].split(":")[0][1:])
            buggy_method[buggy_line_id] = "<START_BUG> " + buggy_method[buggy_line_id].strip() + " <END_BUG>" + '\n'
            clean_method = []
            for line in buggy_method:
                if len(line.strip()) == 0:
                    continue
                clean_method.append(line)
            current_bug_names.append(bug)
            current_bug_ids.append(id)
            current_buggy_methods.append(''.join(clean_method))
            current_buggy_lines.append(buggy_line)
            current_develop_patch_lines.append(develop_patch_line)
        bug_names=bug_names+current_bug_names
        bug_ids=bug_ids+current_bug_ids
        buggy_methods=buggy_methods+current_buggy_methods
        buggy_lines=buggy_lines+current_buggy_lines
        develop_patch_lines=develop_patch_lines+current_develop_patch_lines
    data_frame=pandas.DataFrame({"Bug-name":bug_names,"Bug-Id":bug_ids,"Buggy-Method":buggy_methods,"Buggy-Line":buggy_lines,
                                 "Develop-Patch-Line":develop_patch_lines})
    data_frame.to_excel("bears_data.xlsx",engine="xlsxwriter")
#prepare_Bears("Bears.json","E:/NPR4J/RawData (2)/Benchmarks")
def prepare_quixbugs(ids_f,input_dir):
    ids=readF2L(ids_f)
    bug_names=[]
    bug_ids=[]
    buggy_methods=[]
    buggy_lines=[]
    develop_patch_lines=[]
    for id in ids:
        meta_infos=codecs.open(input_dir+'/metas/'+id+'.txt','r',encoding='utf8').read().strip().split("<sep>")
        buggy_method=readF2L_nostrip(input_dir+'/buggy_methods/'+id+'.txt')
        buggy_line_id=int(meta_infos[2].split(":")[0][1:])
        buggy_method[buggy_line_id]="<START_BUG> "+buggy_method[buggy_line_id].strip()+" <END_BUG>"+'\n'
        clean_method=[]
        for line in buggy_method:
            if len(line.strip())==0:
                continue
            clean_method.append(line)
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        fix_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        bug_name=meta_infos[-1].split("@")[0].split('\\')[-1].replace(".java",'')

        bug_names.append(bug_name)
        bug_ids.append(id)
        buggy_methods.append(''.join(clean_method))
        buggy_lines.append(buggy_line)
        develop_patch_lines.append(fix_line)
        print(id)

    data_frame=pandas.DataFrame({"Bug-name":bug_names,"Bug-Id":bug_ids,"Buggy-Method":buggy_methods,"Buggy-Line":buggy_lines,
                                 "Develop-Patch-Line":develop_patch_lines})
    data_frame.to_excel("qbs_data.xlsx")
#prepare_quixbugs(r"E:\NPR4J\RawData (2)\Benchmarks\qbs.ids.new","E:/NPR4J/RawData (2)/Benchmarks")
def write_quixbugs_infos(ids_f,input_dir,output_f):
    ids = readF2L(ids_f)
    infos_dict={}
    for id in ids:
        meta_infos = codecs.open(input_dir + '/metas/' + id + '.txt', 'r', encoding='utf8').read().strip().split(
            "<sep>")

        buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + '.txt', 'r', encoding='utf8').read().strip()
        fix_line = codecs.open(input_dir + '/fix_lines/' + id + '.txt', 'r', encoding='utf8').read().strip()
        bug_name = meta_infos[-1].split("@")[0].split('\\')[-1].replace(".java", '')
        infos_dict[bug_name]={"buggy_line":buggy_line,"patch_line":fix_line}
        print(id)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(infos_dict,f,indent=2)
#write_quixbugs_infos(r"E:\NPR4J\RawData (2)\Benchmarks\qbs.ids.new","E:/NPR4J/RawData (2)/Benchmarks",
                     #r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info")

def write_bears_infos(ids_f,input_dir,output_f):
    ids=readF2L(ids_f)
    infos_all={}
    for id in ids:
        id_infos={}
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt','r',encoding='utf8').read()
        fix_line = codecs.open(input_dir + '/fix_lines/' + id + '.txt', 'r', encoding='utf8').read()
        id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
        buggy_line_id = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
        buggy_method_lines=readF2L_nostrip(input_dir+'/buggy_methods/'+id+'.txt')
        buggy_method=codecs.open(input_dir+'/buggy_methods/'+id+'.txt','r',encoding='utf8').read()
        appear_times=buggy_method.count(buggy_line)
        assert appear_times>=1
        if appear_times==1:
            prefix=buggy_method.split(buggy_line)[0]
            postfix=buggy_method.split(buggy_line)[1]
        else:
            true_error_count=1
            for idx,line in enumerate(buggy_method_lines):
                if idx < buggy_line_id:
                    count=line.count(buggy_line)
                    true_error_count+=count
            try:
                patterns=buggy_method.split(buggy_line)
                prefix=buggy_line.join(patterns[:true_error_count])
                postfix=buggy_line.join(patterns[true_error_count:])
            except:
                print(id)
                continue
        assert prefix in buggy_method
        assert postfix in buggy_method
        id_infos["buggy_line"]=buggy_line.strip()
        id_infos["developer_line"]=fix_line.strip()
        id_infos["prefix"]=prefix
        id_infos["postfix"]=postfix
        infos_all[id]=id_infos
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(infos_all,f,indent=2)
#write_bears_infos(r"E:\NPR4J\RawData (2)\Benchmarks\bears.ids.new","E:/NPR4J/RawData (2)/Benchmarks","D:/NPR4J-Eval-Results/manual_check/bears.infos")
write_bears_infos(r"E:\NPR4J\RawData (2)\Benchmarks\d4j.ids.new","E:/NPR4J/RawData (2)/Benchmarks","D:/NPR4J-Eval-Results/manual_check/d4j.info")


