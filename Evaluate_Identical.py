import codecs
import json
import os
import re

from Utils.IOHelper import readF2L


def check_identical(label,candidates):
    hit_idx=-1
    pattern = re.compile(r'\s+');
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
                    continue
        else:
            eval_result[id] = -1
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(eval_result, f, indent=2)
Evaluate_identical_Recoder("D:/NPR4J-Pred/qbs/recoder",r"D:\RawData_Processed\SequenceR\qbs.sids",
                           r"D:\RawData_Processed\CodeBERT-ft\qbs.fix",r"D:\NPR4J-Eval-Results\qbs\Recoder\identical.ids")