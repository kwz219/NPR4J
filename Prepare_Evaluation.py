import codecs
import json

from Utils.IOHelper import readF2L


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
def Prepare_SequenceR_patches(cand_size,preds_f,ids_f,input_dir,output_f):
    ids=readF2L(ids_f)
    preds=readF2L(preds_f)
    assert len(ids)*cand_size==len(preds)
    patches_all={}
    for idx,id in enumerate(ids):
        patches_id={}
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+".txt").read().strip()
        buggy_method=codecs.open(input_dir+'/buggy_methods/'+id+'.txt').read().strip()
        all_candidates=preds[idx*cand_size:(idx+1)*cand_size]
        for cid,pred in enumerate(all_candidates):
            patch_method=buggy_method.replace(buggy_line,pred)
            patches_id[str(cid+1)]=patch_method
        patches_all[id]=patches_id
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(patches_all,f,indent=2)
