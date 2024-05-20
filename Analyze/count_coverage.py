import json
import os


def count_APRFix(dir,output_f):
    systems=os.listdir(dir)
    correct_counts={}
    for sys in systems:
        c_list=[]
        patch_dir=dir+'/'+sys
        patches=os.listdir(patch_dir)
        for patch in patches:
            infos=patch.split('_')
            name,state=infos[0],infos[1]
            if infos[1]=="C":
                name=name.replace("-","_")
                c_list.append(name)
        correct_counts[sys]=c_list
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(correct_counts,f,indent=2)

    pass

count_APRFix("D:/文档/icse2023/APR-Efficiency-master/APR-Efficiency-master/Patches/PFL",r"D:\文档\icse2023\APR_fix.json")