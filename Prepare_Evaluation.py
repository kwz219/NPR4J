import codecs
import json
import os

from CoCoNut.tokenization.tokenization import get_strings_numbers, token2statement
from Recovery_Code import Recovery_CoCoNut_one
from Utils.IOHelper import readF2L, readF2L_ori


def Prepare_Tufano_patches(cand_size,recovery_preds_f,output_f,ids_f):
    ids=readF2L(ids_f)
    recovery_preds=readF2L(recovery_preds_f)
    assert len(ids)*cand_size==len(recovery_preds)
    patches_all={}
    for idx,id in enumerate(ids):
        patches_id={}
        preds=recovery_preds[idx*cand_size:(idx+1)*cand_size]
        for pid,pred in enumerate(preds):
            patches_id[str(pid+1)]=pred
        patches_all[id]=patches_id
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(patches_all,f,indent=2)
#Prepare_Tufano_patches(300,"D:/NPR4J-Pred/bears/Tufano/Tufano_b300_bears.pred.recovery",
                      #"D:/NPR4J-Pred/bears/Tufano/Tufano_b300_bears.patches","D:/RawData_Processed/Tufano/bears_test.sids")
#Prepare_Tufano_patches(300,"D:/NPR4J-Pred/qbs/Tufano/Tufano_b300_qbs.pred.recovery",
                       #"D:/NPR4J-Pred/qbs/Tufano/Tufano_b300_qbs.patches","D:/RawData_Processed/Tufano/qbs_test.sids")
#Prepare_Tufano_patches(300,"D:/NPR4J-Pred/d4j/Tufano/Tufano_b300_d4j.pred.recovery",
                       #"D:/NPR4J-Pred/d4j/Tufano/Tufano_b300_d4j.patches","D:/RawData_Processed/Tufano/d4j_test.sids")
#Prepare_Tufano_patches(300,"/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_bears.bdj.recovery",
                       #"/home/zhongwenkang/NPR4J4Eval/Tufano/Tufano_b300_bdj.patches","/home/zhongwenkang/RawData_Processed/Tufano/bdj_test.sids")
def Prepare_patches_fromline(cand_size,preds_f,ids_f,input_dir,output_f):
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    assert len(ids)*cand_size==len(preds)
    patches_all={}
    for idx,id in enumerate(ids):
        patches_id={}
        id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
        err_line=int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+".txt").read().strip()
        buggy_method=readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
        assert (buggy_line in buggy_method[err_line])
        all_candidates=preds[idx*cand_size:(idx+1)*cand_size]
        for cid,pred in enumerate(all_candidates):
            buggy_method[err_line]=pred
            patch_method='\n'.join(buggy_method)
            patches_id[str(cid+1)]=patch_method
        patches_all[id]=patches_id
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(patches_all,f,indent=2)

def Prepare_SequenceR_patches(cand_size,preds_f,ids_f,input_dir,output_f):
    Prepare_patches_fromline(cand_size,preds_f,ids_f,input_dir,output_f)
#Prepare_SequenceR_patches(300,"/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_d4j.pred",
                          #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/d4j.ids.new",
                          #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_d4j.patches")
#Prepare_SequenceR_patches(cand_size=300,preds_f="/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_bears.pred",
                          #ids_f="/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/bears.ids.new",
                          #input_dir="/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                          #output_f="/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_bears.patches")
#Prepare_SequenceR_patches(300,"/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_qbs.pred",
                          #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/qbs.ids.new",
                          #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang2/NPR4J_Pred/SequenceR/SequenceR_b300_qbs.patches")
#Prepare_SequenceR_patches(300,"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_bears.pred",
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks/bears.ids.new"
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_bears.patches")
#Prepare_SequenceR_patches(300,"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_d4j.pred",
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks/d4j.ids.new"
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_d4j.patches")
#Prepare_SequenceR_patches(300,"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_qbs.pred",
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks/qbs.ids.new"
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_qbs.patches")
def Prepare_CodeBERTFT_patches(cand_size,preds_f,ids_f,input_dir,output_f):
    ids = readF2L(ids_f)
    preds = readF2L(preds_f)
    assert len(ids) * cand_size == len(preds)
    patches_all = {}
    for idx, id in enumerate(ids):
        patches_id = {}
        id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
        err_line = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
        buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + ".txt").read().strip()
        buggy_method = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
        assert (buggy_line in buggy_method[err_line])
        all_candidates = preds[idx * cand_size:(idx + 1) * cand_size]
        for cid, pred in enumerate(all_candidates):
            pred=pred.replace("<PRED_START>",'').replace("<PRED_END>",'')
            buggy_method[err_line] = pred
            patch_method = '\n'.join(buggy_method)
            patches_id[str(cid + 1)] = patch_method
        patches_all[id] = patches_id
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(patches_all, f, indent=2)
#Prepare_CodeBERTFT_patches(300,"/home/zhongwenkang2/RawData_Processed/CodeBERT-ft/qbs.output",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/qbs.ids.new",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang2/NPR4J_Pred/CodeBERT-ft/CodeBERT-ft_b300_qbs.patches")
#Prepare_CodeBERTFT_patches(300,"/home/zhongwenkang2/RawData_Processed/CodeBERT-ft/bears.output",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/bears.ids.new",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang2/NPR4J_Pred/CodeBERT-ft/CodeBERT-ft_b300_bears.patches")
#Prepare_CodeBERTFT_patches(300,"/home/zhongwenkang2/RawData_Processed/CodeBERT-ft/d4j.output",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/d4j.ids.new",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang2/NPR4J_Pred/CodeBERT-ft/CodeBERT-ft_b300_d4j.patches")
#Prepare_CodeBERTFT_patches(300,"/home/zhongwenkang2/RawData_Processed/CodeBERT-ft/bdj.output",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks/bdj.ids.new",
                           #"/home/zhongwenkang2/RawData/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang2/NPR4J_Pred/CodeBERT-ft/CodeBERT-ft_b300_bdj.patches")
def Prepare_CoCoNut_patches(cand_size,preds_f,ids_f,input_dir,output_f):
    def Recovery_CoCoNut_one(buggy_str, pred_str):
        strings, numbers = get_strings_numbers(buggy_str)
        recovery_tokens = pred_str.split()
        recovery_str = token2statement(recovery_tokens, numbers, strings)
        # print(recovery_str)
        if len(recovery_str) == 0:
            recovery_str = [pred_str]
        return recovery_str[0]
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    assert len(ids)*cand_size==len(preds)
    patches_all = {}
    for idx,id in enumerate(ids):
        patches_id = {}
        id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
        err_line = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
        buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + ".txt").read().strip()
        buggy_method = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
        assert (buggy_line in buggy_method[err_line])
        all_candidates = preds[idx * cand_size:(idx + 1) * cand_size]
        for cid, pred in enumerate(all_candidates):
            recover_pred=Recovery_CoCoNut_one(buggy_line,pred)
            buggy_method[err_line] = recover_pred
            patch_method = '\n'.join(buggy_method)
            patches_id[str(cid + 1)] = patch_method
        patches_all[id] = patches_id
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(patches_all, f, indent=2)
def prepare_CoCoNut_patches_all(cand_size,buggy_f,preds_dir,ids_f,input_dir,output_f):

    ids=readF2L(ids_f)
    patches_all={}
    buggy_lines=readF2L(buggy_f)
    assert len(buggy_lines)==len(ids)
    patches_final={}
    for id in ids:
        patches_final[id]=[]
    ensemble_list=os.listdir(preds_dir)
    for file in ensemble_list:
        preds=readF2L(preds_dir+'/'+file)
        for pred in preds:
            if pred.startswith("H"):
                id,prob,pred=pred.strip().split('\t')
                bugID=ids[int(id.split('-')[1])]
                buggy_line=buggy_lines[int(id.split('-')[1])]
                tuple_list=patches_final[bugID]
                tuple_list.append((float(prob),Recovery_CoCoNut_one(buggy_line,pred)))
                patches_final[bugID]=tuple_list
    for id in patches_final.keys():
        tuple_list=patches_final[id]
        print(id)
        sorted_list=sorted(tuple_list,key=lambda t:t[0],reverse=True)
        id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
        err_line = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
        buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + ".txt").read().strip()
        buggy_method = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
        assert (buggy_line in buggy_method[err_line])
        final_dict={}
        ind=1
        checkset=set()
        for (prob,pred) in sorted_list:
            if pred not in checkset:
                buggy_method[err_line] = pred
                patch_method = '\n'.join(buggy_method)
                final_dict[str(ind)]=patch_method
                checkset.add(pred)
                ind+=1
                if ind >cand_size:
                    break
        patches_all[id]=final_dict
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(patches_all, f, indent=2)

prepare_CoCoNut_patches_all(300,r"D:\RawData_Processed\CodeBERT-ft\qbs.buggy","D:/NPR4J-Pred/qbs/CoCoNut",r"D:\RawData_Processed\SequenceR\qbs.sids",
                            "E:/NPR4J/RawData (2)/Benchmarks",r"D:\NPR4J-Eval-Results\qbs\CoCoNut\CoCoNut_300.patches")

def prepare_Recoder_patches(pred_dir,output_f,id_prefix=""):
    files=os.listdir(pred_dir)
    patches_all={}
    for file in files:
        if not file.endswith(".fix"):
            continue
        id =file.split(".")[0]
        if id_prefix in ["qbs","d4j","bears"]:
            id=id_prefix+"_"+id
        patches_id={}
        predictions=json.load(codecs.open(pred_dir+'/'+file,'r',encoding='utf8'))
        for key in predictions.keys():
            new_key=int(key)+1
            patches_id[str(new_key)]=predictions[key]
        patches_all[id]=patches_id
    with open(output_f, 'w', encoding='utf8') as f:
        json.dump(patches_all, f, indent=2)
#prepare_Recoder_patches("D:/NPR4J-Pred/d4j/recoder","D:/NPR4J-Eval/d4j/recoder_b300.patches")
#prepare_Recoder_patches("D:/NPR4J-Pred/qbs/recoder","D:/NPR4J-Eval-Results/qbs/Recoder/recoder.patches","qbs")
#prepare_Recoder_patches("D:/NPR4J-Pred/bears/recoder","D:/NPR4J-Eval-Results/bears/Recoder/recoder.patches","bears")