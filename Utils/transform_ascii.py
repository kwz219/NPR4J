import codecs
import json


def transform_bears_json(bears_f):
    bears_origin=json.load(codecs.open(bears_f,'r',encoding='utf8'))
    for bug in bears_origin.keys():
        ids_info=bears_origin[bug]
        for id in ids_info.keys():
            id_info=ids_info[id]
            ori_class=id_info["classcontent"]
            raw_method=id_info["buggy_method"]
            new_class=ori_class.replace('\r\r\n','\n\n').replace('\r\n','\n')
            if raw_method in new_class:
                print("in")
            else:
                print("not")
            ids_info[id]["classcontent"]=new_class
    with open("Bears.json",'w',encoding='utf8')as f:
        json.dump(bears_origin,f,indent=2)

transform_bears_json(r"D:\bears.json")