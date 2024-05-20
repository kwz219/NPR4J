import codecs
import json

import pandas

def check_list_bears(infos_f,identical_ids_f,sys,bears_info2,preds_f,output_dir):
    infos = json.load(codecs.open(infos_f, 'r', encoding='utf8'))
    identical = json.load(codecs.open(identical_ids_f, 'r', encoding='utf8'))
    meta_infos = json.load(codecs.open(bears_info2, 'r', encoding='utf8'))
    preds = json.load(codecs.open(preds_f, 'r', encoding='utf8'))
    bug_names = []
    bug_ids = []
    systems = []
    buggy_lines = []
    fix_lines = []
    pred_patches = []
    patch_indexes = []
    for bug in infos:
        skip_flag = 0
        bug_info = infos[bug]
        ids = []
        for key in bug_info.keys():
            ids.append(key)

        dict = {}
        for id in ids:

            if id in identical.keys():
                if int(identical[id]) > -1:
                    dict[id] = identical[id]
                    bug_names.append(bug)
                    bug_ids.append(id)
                    systems.append(sys)
                    meta_info = meta_infos[id]
                    buggy_lines.append(meta_info["buggy_line"])
                    fix_lines.append(meta_info["developer_line"])
                    prefix = meta_info["prefix"].strip()
                    postfix = meta_info["postfix"].strip()
                    if not sys in ["Recoder", "Recoder_ori"]:
                        prefix = prefix.replace('\n', '\n\n')
                        postfix = postfix.replace('\n', '\n\n')
                    pred_patch = preds[id][str(identical[id])].replace(prefix, '', 1).replace(postfix, '')
                    pred_patches.append(pred_patch)
                    patch_indexes.append(identical[id])
                else:
                    skip_flag = 1
                    break
        if skip_flag == 1:
            continue
        else:
            print(bug, dict)
    df = pandas.DataFrame({"Bug-Name": bug_names, "Id": bug_ids, "NPR-System": systems, "Buggy-Line": buggy_lines,
                           "Develop-Patch-Line": fix_lines,
                           "Patch-Index": patch_indexes, "Pred-Patch": pred_patches})
    df.to_excel(output_dir + '/bears_' + sys + '.xlsx')
#check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\Recoder\identical.ids",sys="Recoder",
   #bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\Recoder\recoder.patches",
    #output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\Recoder_ori\identical.ids",sys="Recoder_ori",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\Recoder_ori\recoder_ori_b300.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\CoCoNut\identical.ids",sys="CoCoNut",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\CoCoNut\CoCoNut_300.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\CodeBERT-ft\identical.ids",sys="CodeBERT-ft",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\CodeBERT-ft\CodeBERT-ft_b300_bears.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\Edits\identical.ids",sys="Edits",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\Edits\Edits_bears_b300.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\RewardRepair\identical.ids",sys="RewardRepair",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\bears\RewardRepair\bears_mine.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\RewardRepair_ori\identical.ids",sys="RewardRepair_ori",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\bears\RewardRepair_ori\bears_ori.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\Tufano\identical.ids",sys="Tufano",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\bears\NPR-Eval\Tufano_b300_bears.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
check_list_bears("D:/NPR4J/Utils/Bears.json",r"D:\NPR4J-Eval-Results\bears\SequenceR\identical.ids",sys="SequenceR",
   bears_info2=r"D:\NPR4J-Eval-Results\manual_check\bears.info",preds_f=r"D:\NPR4J-Eval-Results\bears\SequenceR\SequenceR_b300_bears.patches",
    output_dir="D:/NPR4J-Eval-Results/identical")
def check_lost_defects4j(infos_f,identical_ids_f,sys,d4j_info2,preds_f,output_dir):
    infos=json.load(codecs.open(infos_f,'r',encoding='utf8'))["d4j"]
    identical=json.load(codecs.open(identical_ids_f,'r',encoding='utf8'))
    meta_infos=json.load(codecs.open(d4j_info2,'r',encoding='utf8'))
    preds=json.load(codecs.open(preds_f,'r',encoding='utf8'))
    bug_names=[]
    bug_ids=[]
    systems=[]
    buggy_lines=[]
    fix_lines=[]
    pred_patches=[]
    patch_indexes=[]
    for bug in infos:
        skip_flag=0
        bug_info=infos[bug]
        ids=[]
        for file in bug_info:
            ids+=bug_info[file]["ids"]

        dict={}
        for id in ids:
            id="d4j_"+id
            if id in identical.keys():
                if int(identical[id])>-1:
                    dict[id]=identical[id]
                    bug_names.append(bug)
                    bug_ids.append(id)
                    systems.append(sys)
                    meta_info=meta_infos[id]
                    buggy_lines.append(meta_info["buggy_line"])
                    fix_lines.append(meta_info["developer_line"])
                    prefix = meta_info["prefix"].strip()
                    postfix = meta_info["postfix"].strip()
                    if not sys in ["Recoder", "Recoder_ori"]:
                        prefix = prefix.replace('\n', '\n\n')
                        postfix = postfix.replace('\n', '\n\n')
                    pred_patch=preds[id][str(identical[id])].replace(prefix,'',1).replace(postfix,'')
                    pred_patches.append(pred_patch)
                    patch_indexes.append(identical[id])
                else:
                    skip_flag=1
                    break
        if skip_flag==1:
            continue
        else:
            print(bug,dict)
    df = pandas.DataFrame({"Bug-Name": bug_names, "Id": bug_ids, "NPR-System": systems, "Buggy-Line": buggy_lines,
                           "Develop-Patch-Line": fix_lines,
                           "Patch-Index": patch_indexes, "Pred-Patch": pred_patches})
    df.to_excel(output_dir + '/d4j_' + sys + '.xlsx')
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\Recoder\identical.ids",sys="Recoder",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder\Recoder_d4j_b300.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")

#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\SequenceR\identical.ids",sys="SequenceR",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\SequenceR\SequenceR_b300_d4j.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\CodeBERT-ft\identical.ids",sys="CodeBERT-ft",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\CodeBERT-ft\CodeBERT-ft_b300_d4j.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\Edits\identical.ids",sys="Edits",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"D:\NPR4J-Eval-Results\d4j\Edits\Edits_d4j_b300.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\CoCoNut\identical.ids",sys="CoCoNut",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"D:\NPR4J-Eval-Results\d4j\CoCoNut\CoCoNut_300_d4j.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\Recoder_ori\identical.ids",sys="Recoder_ori",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder_ori\recoder_ori_b300.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\RewardRepair\identical.ids",sys="RewardRepair",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair\d4j_mine.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
#check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\RewardRepair_ori\identical.ids",sys="RewardRepair_ori",
                     #d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair_ori\d4j_ori.patches",
                     #output_dir="D:/NPR4J-Eval-Results/identical")
check_lost_defects4j(r"D:\Test_Suite_Ori\Test_Suite2\config\infos.json",r"D:\NPR4J-Eval-Results\d4j\Tufano\identical.ids",sys="Tufano",
                     d4j_info2=r"D:\NPR4J-Eval-Results\manual_check\d4j.info",preds_f=r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Tufano\Tufano_b300_d4j.patches",
                     output_dir="D:/NPR4J-Eval-Results/identical")
