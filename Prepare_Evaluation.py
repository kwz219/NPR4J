import codecs
import json

from CoCoNut.tokenization.tokenization import get_strings_numbers, token2statement
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
#Prepare_Tufano_patches(300,"/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_bears.pred.recovery",
                       #"/home/zhongwenkang/NPR4J4Eval/Tufano/Tufano_b300_bears.patches","/home/zhongwenkang/RawData_Processed/Tufano/bears_test.sids")
#Prepare_Tufano_patches(300,"/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_qbs.pred.recovery",
                       #"/home/zhongwenkang/NPR4J4Eval/Tufano/Tufano_b300_qbs.patches","/home/zhongwenkang/RawData_Processed/Tufano/qbs_test.sids")
#Prepare_Tufano_patches(300,"/home/zhongwenkang/NPR4J_Pred/Tufano/Tufano_b300_bears.d4j.recovery",
                       #"/home/zhongwenkang/NPR4J4Eval/Tufano/Tufano_b300_d4j.patches","/home/zhongwenkang/RawData_Processed/Tufano/d4j_test.sids")
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
#Prepare_SequenceR_patches(300,"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_bdj.pred",
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks/bdj.ids.new"
                          #"/home/zhongwenkang/RawData/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/NPR4J_Pred/SequenceR/SequenceR_b300_bdj.patches")
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
    Prepare_patches_fromline(cand_size, preds_f, ids_f, input_dir, output_f)

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


