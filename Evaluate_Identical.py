import codecs
import json
import os
import re

from Utils.IOHelper import readF2L


def check_identical(label,candidates):
    hit_idx=-1
    pattern = re.compile(r'\s+');
    if isinstance(candidates,dict):
        for idx in candidates.keys():
            label_new=re.sub(pattern,'',label)
            cand_new=re.sub(pattern,'',candidates[idx])
            if label_new==cand_new:
                hit_idx=idx
                break
        pass
    else:
        for idx,cand in enumerate(candidates):
            label_new=re.sub(pattern,'',label)
            cand_new=re.sub(pattern,'',cand)
            if label_new==cand_new:
                print(label,cand)
                hit_idx=idx+1
                break
    return hit_idx

    pass
def Evaluate_identical_SequenceR(candidate_size,pred_f,label_f,ids_f,output_f):
    preds=readF2L(pred_f)
    labels=readF2L(label_f)
    ids=readF2L(ids_f)
    assert len(ids)==len(labels)
    assert len(preds)==len(ids)*candidate_size
    eval_result={}
    for idx,id in enumerate(ids):
        label=labels[idx]
        candidates=preds[idx*candidate_size:(idx+1)*candidate_size]
        eval_result[id]=check_identical(label,candidates)
    for id in eval_result.keys():
        if eval_result[id]>0:
            print(id,eval_result[id])
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(eval_result,f,indent=2)
#Evaluate_identical_SequenceR(300,r"D:\NPR4J-Pred\qbs\SequenceR\SequenceR_b300_qbs.pred",r"D:\RawData_Processed\SequenceR\qbs.fix",
                             #r"D:\RawData_New\qbs.ids.new",r"D:\NPR4J-Eval-Results\qbs\SequenceR\identical.ids")
#Evaluate_identical_SequenceR(300,r"D:\NPR4J-Pred\d4j\SequenceR\SequenceR_b300_d4j.pred",r"D:\RawData_Processed\SequenceR\d4j.fix",
                             #r"D:\RawData_New\d4j.ids.new",r"D:\NPR4J-Eval-Results\d4j\SequenceR\identical.ids")
#Evaluate_identical_SequenceR(300,r"D:\NPR4J-Pred\bears\SequenceR\SequenceR_b300_bears.pred",r"D:\RawData_Processed\SequenceR\bears.fix",
                             #r"D:\RawData_New\bears.ids.new",r"D:\NPR4J-Eval-Results\bears\SequenceR\identical.ids")
def Evaluate_identical_Tufano(candidate_size,pred_f,ids_f,label_f,output_f):
    preds=readF2L(pred_f)
    labels=readF2L(label_f)
    ids=readF2L(ids_f)
    assert len(ids)==len(labels)
    assert len(preds)==len(ids)*candidate_size
    eval_result={}
    for idx,id in enumerate(ids):
        label=labels[idx]
        candidates=preds[idx*candidate_size:(idx+1)*candidate_size]
        eval_result[id]=check_identical(label,candidates)
    for id in eval_result.keys():
        if eval_result[id]>0:
            print(id,eval_result[id])
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(eval_result,f,indent=2)
#Evaluate_identical_Tufano(300,r"D:\NPR4J-Pred\qbs\Tufano\Tufano_b300_qbs.pred.recovery","D:/RawData_Processed/Tufano/qbs_test.sids",
                          #"D:/RawData_Processed/Tufano/qbs_test.fix.recovery",r"D:\NPR4J-Eval-Results\qbs\Tufano\identical.ids")
#Evaluate_identical_Tufano(300,r"D:\NPR4J-Pred\d4j\Tufano\Tufano_b300_d4j.pred.recovery","D:/RawData_Processed/Tufano/d4j_test.sids",
                          #"D:/RawData_Processed/Tufano/d4j_test.fix.recovery",r"D:\NPR4J-Eval-Results\d4j\Tufano\identical.ids")
#Evaluate_identical_Tufano(300,r"D:\NPR4J-Pred\bears\Tufano\Tufano_b300_bears.pred.recovery","D:/RawData_Processed/Tufano/bears_test.sids",
                          #"D:/RawData_Processed/Tufano/bears_test.fix.recovery",r"D:\NPR4J-Eval-Results\bears\Tufano\identical.ids")
def Evaluate_identical_CodeBERTft(candidate_size,pred_f,ids_f,label_f,output_f):
    preds=readF2L(pred_f)
    labels=readF2L(label_f)
    ids=readF2L(ids_f)
    assert len(ids)==len(labels)
    assert len(preds)==len(ids)*candidate_size
    eval_result={}
    rec_preds=[]
    for pred in preds:
        pure_pred=pred.replace("<PRED_START>","").replace("<PRED_END>","")
        rec_preds.append(pure_pred)
    for idx,id in enumerate(ids):
        label=labels[idx]
        candidates=rec_preds[idx*candidate_size:(idx+1)*candidate_size]
        eval_result[id]=check_identical(label,candidates)
    for id in eval_result.keys():
        if eval_result[id]>0:
            print(id,eval_result[id])
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(eval_result,f,indent=2)
#Evaluate_identical_CodeBERTft(300,r"D:\NPR4J-Pred\qbs\CodeBERT-ft\qbs.output","D:/RawData_Processed/Tufano/qbs_test.sids",
                          #"D:/RawData_Processed/CodeBERT-ft/qbs.fix",r"D:\NPR4J-Eval-Results\qbs\CodeBERT-ft\identical.ids")
#Evaluate_identical_CodeBERTft(300,r"D:\NPR4J-Pred\d4j\CodeBERT-ft\d4j.output","D:/RawData_Processed/SequenceR/d4j.sids",
 #"D:/RawData_Processed/CodeBERT-ft/d4j.fix",r"D:\NPR4J-Eval-Results\d4j\CodeBERT-ft\identical.ids")

#Evaluate_identical_CodeBERTft(300,r"D:\NPR4J-Pred\bears\CodeBERT-ft\bears.output","D:/RawData_Processed/SequenceR/bears.sids",
                          #"D:/RawData_Processed/CodeBERT-ft/bears.fix",r"D:\NPR4J-Eval-Results\bears\CodeBERT-ft\identical.ids")
def Evaluate_identical_Recoder(preds_dir,ids_f,labels_f,output_f):
    ids=readF2L(ids_f)
    labels=readF2L(labels_f)
    eval_result = {}
    pattern = re.compile(r'\s+');
    for idx,id in enumerate(ids):
        label=labels[idx]
        fix_id=id.split('_')[-1]
        fix_path=preds_dir+'/'+fix_id+'.fix'
        pure_label=re.sub(pattern,'',label)
        #print(pure_label)
        eval_result[id] = -1
        if os.path.exists(fix_path):
            candidates=json.load(codecs.open(fix_path,'r',encoding='utf8'))
            for key in candidates.keys():
                cand=candidates[key]
                pure_cand=re.sub(pattern,'',cand)

                if pure_label in pure_cand:
                    eval_result[id] = int(key)+1
                    break
        else:
            eval_result[id] = -1
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(eval_result, f, indent=2)

def Evaluate_identical_Recoder_2(preds_f,methods_dir,output_f):
    preds=json.load(codecs.open(preds_f,'r',encoding='utf8'))
    pattern = re.compile(r'\s+');
    eval_result = {}
    for id in preds.keys():
        candidates=preds[id]
        eval_result[id] = -1
        for key in candidates.keys():
            key_candidate=candidates[key]
            fix_method=codecs.open(methods_dir+'/'+id+'.txt','r',encoding='utf8').read()
            pure_cand = re.sub(pattern, '', key_candidate)
            pure_fix=re.sub(pattern,'',fix_method)
            pure_cand=pure_cand.replace('(','').replace(')','')
            pure_fix=pure_fix.replace('(','').replace(')','')
            if pure_cand==pure_fix:
                eval_result[id]=int(key)
                break
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(eval_result, f, indent=2)

#Evaluate_identical_Recoder("D:/NPR4J-Pred/qbs/recoder",r"D:\RawData_Processed\SequenceR\qbs.sids",
                           #r"D:\RawData_Processed\CodeBERT-ft\qbs.fix",r"D:\NPR4J-Eval-Results\qbs\Recoder\identical.ids")
#Evaluate_identical_Recoder("D:/NPR4J-Pred/d4j/recoder_2",r"D:\RawData_Processed\SequenceR\d4j.sids",
                           #r"D:\RawData_Processed\CodeBERT-ft\d4j.fix",r"D:\NPR4J-Eval-Results\d4j\Recoder\identical.ids")
#Evaluate_identical_Recoder_2(r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder\Recoder_d4j_b300.patches",
                           #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\Recoder\identical.ids")
#Evaluate_identical_Recoder_2(r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\Recoder_ori\recoder_ori_b300.patches","E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\Recoder_ori\identical.ids")
#Evaluate_identical_Recoder_2(r"D:\NPR4J-Eval-Results\bears\Recoder\recoder.patches","E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\Recoder\identical.ids")
#Evaluate_identical_Recoder_2(r"D:\NPR4J-Eval-Results\bears\Recoder_ori\recoder_ori_b300.patches","E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\Recoder_ori\identical.ids")
def Evaluate_identical_CoCoNut(ids_f,patches_f,fix_methods_dir,output_f):
    candidates=json.load(codecs.open(patches_f,'r',encoding='utf8'))
    ids=readF2L(ids_f)
    eval_result={}
    for id in ids:
        eval_result[id]=-1
        id_preds=candidates[id]
        fix_method=codecs.open(fix_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip()
        #print(fix_method,id_preds["1"])
        identical_re=check_identical(fix_method,id_preds)
        eval_result[id]=identical_re
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(eval_result, f, indent=2)
#Evaluate_identical_CoCoNut(r"D:\RawData_Processed\SequenceR\qbs.sids",r"D:\NPR4J-Eval-Results\qbs\CoCoNut\CoCoNut_300.patches",
                           #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\qbs\CoCoNut\identical.ids")
#Evaluate_identical_CoCoNut(r"D:\RawData_Processed\SequenceR\d4j.sids",r"D:\NPR4J-Eval-Results\d4j\CoCoNut\CoCoNut_300_d4j.patches",
                           #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\CoCoNut\identical.ids")
Evaluate_identical_CoCoNut(r"D:\RawData_Processed\SequenceR\bears.sids",r"D:\NPR4J-Eval-Results\bears\CoCoNut\CoCoNut_300.patches",
                           "E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\CoCoNut\identical.ids")
def Evaluate_identical_Edits(ids_f,patches_f,fix_methods_dir,output_f):
    candidates=json.load(codecs.open(patches_f,'r',encoding='utf8'))
    ids=readF2L(ids_f)
    eval_result={}
    for id in ids:
        eval_result[id]=-1
        id_preds=candidates[id]
        fix_method=codecs.open(fix_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip()
        #print(fix_method,id_preds["1"])
        identical_re=check_identical(fix_method,id_preds)
        eval_result[id]=identical_re
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(eval_result, f, indent=2)

#Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\qbs.ids",r"D:\NPR4J-Pred\qbs\Edits\Edits_qbs_b300.patches",
                         #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\qbs\Edits\identical.ids")
#Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\d4j.ids",r"D:\NPR4J-Pred\d4j\Edits\Edits_d4j_b300.patches",
                         #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\Edits\identical.ids")
#Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\d4j.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair\d4j_mine.patches",
                         #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\RewardRepair\identical.ids")
#Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\d4j.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair_ori\d4j_ori.patches",
                         #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\RewardRepair_ori\identical.ids")
#Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\bears.ids",r"D:\NPR4J-Pred\bears\Edits\Edits_bears_b300.patches",
   #"E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\Edits\identical.ids")
# Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\d4j.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair\d4j_mine.patches",
# "E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\RewardRepair\identical.ids")
# Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\d4j.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\d4j\RewardRepair_ori\d4j_ori.patches",
# "E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\d4j\RewardRepair_ori\identical.ids")
Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\bears.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\bears\RewardRepair_ori\bears_ori.patches",
   "E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\RewardRepair_ori\identical.ids")
Evaluate_identical_Edits(r"D:\RawData_Processed\PatchEdits\bears.ids",r"E:\NPR4J\ICSE23\NPR4J_Eval\bears\RewardRepair\bears_mine.patches",
   "E:/NPR4J/RawData (2)/Benchmarks/fix_methods",r"D:\NPR4J-Eval-Results\bears\RewardRepair\identical.ids")