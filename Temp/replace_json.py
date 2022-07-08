import codecs
import json


def replace_d4j_jsons(infos_f,source_dir,target_dir):
    infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))
    d4j_infos=infos["d4j"]
    for bug in d4j_infos.keys():
        replace_ids=[]
        bug_infos=d4j_infos[bug]
        for file in bug_infos.keys():
            idlist=bug_infos[file]["ids"]
            replace_ids+=idlist
        bug=bug.replace('_','-')
        bug_json=json.load(codecs.open(source_dir+'/'+bug+'.json','r',encoding='utf8'))
        for id in replace_ids:
            json.dump(bug_json,codecs.open(target_dir+'/d4j_'+id+'.json','w',encoding='utf8'),indent=2)
replace_d4j_jsons(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json","D:/RawData_Processed/Recoder_d4j_ori","D:/RawData_Processed/Recoder_replace")
