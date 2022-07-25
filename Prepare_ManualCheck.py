import codecs
import json
import os

import pandas

from Utils.IOHelper import readF2L, readF2L_ori


def prepare_QuixBugs_for_check(quixbugs_info_f,patch_dir,sys,outout_dir):
    quixbug_infos=json.load(codecs.open(quixbugs_info_f,'r',encoding='utf8'))
    files=os.listdir(patch_dir)
    def get_pred_line(patch_f,sys):
        if not sys == "Tufano":
            patch_lines=readF2L_ori(patch_f)
            for line in patch_lines:
                if line.lstrip()==line:
                    return line
        else:
            patch_method=codecs.open(patch_f,'r',encoding='utf8').read().strip()
            return patch_method
        return "parse_error"
    tool_names=[]
    bug_names=[]
    buggy_lines=[]
    develop_patch_lines=[]
    patch_indexes=[]
    pred_lines=[]
    for file in files:
        if file.endswith(".patch"):
            infos=file.split("_")
            #tool_name=infos[0]
            tool_name=sys
            if len(infos)==4:
                bug_name=infos[1]
            else:
                bug_name="_".join(infos[1:-2])

                bug_name=bug_name.replace("ori_","")
            print(bug_name)
            patch_index=int(infos[-1].replace(".patch",''))
            pred_patch=get_pred_line(patch_dir+'/'+file,sys)
            buggy_line=quixbug_infos[bug_name]["buggy_line"]
            develop_patch_line=quixbug_infos[bug_name]["patch_line"]

            tool_names.append(tool_name)
            bug_names.append(bug_name)
            buggy_lines.append(buggy_line)
            develop_patch_lines.append(develop_patch_line)
            patch_indexes.append(patch_index)
            pred_lines.append(pred_patch)
    df=pandas.DataFrame({"Bug-Name":bug_names,"NPR-System":tool_names,"Buggy-Line":buggy_lines,"Develop-Patch-Line":develop_patch_lines,
                         "Patch-Index":patch_indexes,"Pred-Patch":pred_lines})
    df.to_excel(outout_dir+'/qbs_'+sys+'.xlsx')

#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/SequenceR",
                           #"SequenceR","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/CoCoNut",
                           #"CoCoNut","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/CodeBERT-ft",
                           #"CodeBERT-ft","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Edits",
                           #"Edits","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Recoder",
                           #"Recoder","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Recoder_ori",
                           #"Recoder_ori","D:/NPR4J-Eval-Results/manual_check")
#prepare_QuixBugs_for_check(r"D:\NPR4J-Eval-Results\manual_check\quixbugs.info","D:/NPR4J-Eval-Results/qbs/Tufano",
                           #"Tufano","D:/NPR4J-Eval-Results/manual_check")
