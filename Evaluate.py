import json
import os.path

from Utils.IOHelper import readF2L, writeL2F, readF2L_enc
import codecs

def acc_simple(ids_f,preds_f,labels_f,results_dir,nbest=10):
    ids=readF2L(ids_f)
    enc="iso8859-1"
    preds=readF2L_enc(preds_f,enc)
    labels=readF2L_enc(labels_f,enc)
    print(len(ids),len(preds),len(labels))
    assert len(preds)==len(labels)*nbest and len(labels)==len(ids)
    results_perid=[]
    acc_count={"acc1":0,"acc5":0,"acc10":0}
    total_count=0
    for i,id in enumerate(ids):
        label=labels[i]
        pred=preds[i*nbest:i*nbest+nbest]
        acc_1=int(label.strip() == pred[0].strip())
        acc_count["acc1"]=acc_count["acc1"]+acc_1
        acc_5=int(hit(label,pred[:5]))
        acc_count["acc5"] = acc_count["acc5"] + acc_5
        acc_10=int(hit(label,pred[:10]))
        acc_count["acc10"] = acc_count["acc10"] + acc_10
        print(i,acc_count)
        results_perid.append(id+" "+str(acc_1)+" "+str(acc_5)+" "+str(acc_10))
    for key in acc_count.keys():
        acc_count[key]=acc_count[key]/len(labels)
    print(acc_count)
    writeL2F(results_perid,results_dir+"/results_perid.txt")
def acc_CoCoNut(predf,results_dir,nbest=10):
    preds=readF2L(predf)
    step=nbest*2+2
    results_perid=[]
    acc_count={"acc1":0,"acc5":0,"acc10":0}
    def get_preds(hps):
        assert len(hps)%2==0
        final_preds=[]
        for i in range(0,len(hps),2):
            pred=' '.join(hps[i].split()[3:])
            final_preds.append(pred)
        return final_preds
    stepcount=0
    for i in range(0,len(preds),step):
        src=' '.join(preds[i].split()[1:])
        label=' '.join(preds[i+1].split()[1:])
        #print("src",src)
        #print("label",label)
        n_pred=preds[i+2:i+step]
        pred=get_preds(n_pred)
        #print(len(pred))
        #print('---------')
        acc_1=int(label in pred[0])
        acc_count["acc1"]=acc_count["acc1"]+acc_1
        acc_5=int(label in ' '.join(pred[:5]))
        acc_count["acc5"] = acc_count["acc5"] + acc_5
        acc_10=int(label in ' '.join(pred[:10]))
        acc_count["acc10"] = acc_count["acc10"] + acc_10
        print(i,acc_count)
        results_perid.append(src+" "+str(acc_1)+" "+str(acc_5)+" "+str(acc_10))
    for key in acc_count.keys():
        acc_count[key]=acc_count[key]/(len(preds)/step)
    print(acc_count)
    writeL2F(results_perid,results_dir+"/results_perid.txt")
def analyze_mismatch(ids_f,ids_f2,fix_abs_dir,pred,buggy_abs_dir):
    ids=readF2L(ids_f)
    ids2=readF2L(ids_f2)
    idset2=set()
    idset=set()
    idslist=[]
    for idinfo in ids2:
        infos=idinfo.split()
        idslist.append(infos[0])
        if int(infos[1])==1:
            idset2.add(infos[0])
    for idinfo in ids:
        infos=idinfo.split()
        if int(infos[1])==1:
            idset.add(infos[0])
    mismatch_set=idset2-idset
    preds=readF2L(pred)
    print(len(preds),len(idslist))
    #print(idslist)
    for id in mismatch_set:
        fix_abs=codecs.open(fix_abs_dir+'/'+id+"_fix.txt.abs",'r',encoding='utf8').read()
        fix_abs_map=json.load(codecs.open(fix_abs_dir+'/'+id+"_fix.txt.abs.map",'r',encoding='utf8'))
        pred_abs_map = json.load(codecs.open(buggy_abs_dir + '/' + id + "_buggy.txt.abs.map", 'r', encoding='utf8'))
        fix_pred=preds[idslist.index(id)*10]
        print(id)
        print(fix_abs)
        print(fix_pred)
        print(fix_abs_map)
        print(pred_abs_map)
        print("------------------------------")


def hit(label,preds):
    for pred in preds:
        if label.strip()==pred.strip():
            return 1
    return 0
def acc_Tufano(src_pred,src_ids,src_absdir,label_dir,nbest=10):
    ids=readF2L(src_ids)
    preds=readF2L(src_pred)
    def reverse_map(ori_map):
        reversed_map={}
        for key in ori_map.keys():
            value=ori_map[key]
            reversed_map[value]=key
        return reversed_map
    def get_originlabel(label,map_f):
        map_file=codecs.open(map_f, 'r', encoding='iso8859-1')
        map=json.load(map_file)
        map=reverse_map(map)
        for key in map.keys():
            if key in label:
                label = label.replace(key,map[key])
        return label
    print(len(ids),len(preds))
    assert len(ids)*nbest==len(preds)
    results_perid=[]
    acc_count={"acc1":0,"acc5":0,"acc10":0}
    total_count=0
    for i,id in enumerate(ids):
        #print(id)
        label_f=label_dir+"/"+id+"_fix.txt.abs"
        #print(label_f)
        map_f=label_dir+"/"+id+"_fix.txt.abs.map"
        bug_map_f=src_absdir+"/"+id+"_buggy.txt.abs.map"
        if not os.path.exists(label_f):
            label_f=label_f.replace('test','val')
            map_f = map_f.replace('test', 'val')
        if not os.path.exists(label_f):
            label_f=label_f.replace('val','trn')
            map_f = map_f.replace('val', 'trn')
        if not os.path.exists(label_f):
            results_perid.append(id + " label not exists" )
            continue
        try:
            true_label = codecs.open(label_f, 'r').read()
            true_label=get_originlabel(true_label,map_f)
        except:
            results_perid.append(id + " parse error")
            continue
        #print(true_label)

        try:
            true_preds=preds[i*nbest:i*nbest+nbest]
            true_preds=[get_originlabel(pred,bug_map_f) for pred in true_preds ]
        except:
            results_perid.append(id + " parse error")
            continue
        if len(true_label.split())>1:
            total_count+=1
            acc_1=int(true_label.strip() == true_preds[0].strip())
            acc_count["acc1"]=acc_count["acc1"]+acc_1
            acc_5=int(hit(true_label,true_preds[:5]))
            acc_count["acc5"] = acc_count["acc5"] + acc_5
            acc_10=int(hit(true_label,true_preds[:10]))
            acc_count["acc10"] = acc_count["acc10"] + acc_10
            print(i,acc_count)
            results_perid.append(id+" "+str(acc_1)+" "+str(acc_5)+" "+str(acc_10))
    for key in acc_count.keys():
        acc_count[key]=acc_count[key]/total_count if total_count>0 else 0
    print(acc_count)
    writeL2F(results_perid,src_pred+".resultids")
#acc_CoCoNut(r"G:\DDPR\Artifacts\\20889_CoCoNut_o9\20878_CoCoNut_o1_translate_nb10.pred")
#acc_CoCoNut(r"G:\DDPR\Artifacts\20878_CoCoNut_o9\20878_CoCoNut_o1_translate_nb10.pred")
#acc_Tufano("G:\DDPR\Artifacts\\20878_CATufano_idiom10w_transformer+copy_wv512\\20878_CATufano_idiom10w_transformer+copywv512best_b10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test","E:\APR_data\data\Tufano_idiom10w\\test")
#acc_Tufano("G:\DDPR\Artifacts\\20873_Tufano_wv512_base64+copy\\20873_Tufano_copy_step_100000.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
#acc_Tufano("G:\DDPR\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test\\abs_correct.txt","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt")
#acc_Tufano("D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\20878_Tufano_idioms2w_best_nb10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
#acc_Tufano("D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\20878_Tufano_idioms2w_best_nb10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
#acc_simple("D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR/test.sids",r"G:\DDPR\Artifacts\20878_SequenceR_origin\20878_SR_origin_best_b10.pred",
           #"D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\test.fix",
           #r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\20878_SequenceR_origin",nbest=10)
#acc_simple("D:/DDPR_DATA/OneLine_Replacement/M1000_Tjava/test.sids",r"G:\DDPR\Artifacts\20890_CANone_transformer_wv512\20890_CANone_transformerwv512_best_b10.pred",
           #"D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava\\test.fix",
           #r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\\20890_CANone_transformer_wv512",nbest=10)
if __name__ =="__main__":
    info_20878_CATufano_idiom10w_transformer_wv512={"pred":"G:\DDPR_backup\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred",
                                                    "ids":"D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test\\abs_correct.txt",
                                                    "src_absdir":"D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)",
                                                    "label_dir":"D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt"}
    info_20878_CATufano_idiom10w_transformer_wv512_copy = {
        "pred": "G:\DDPR_backup\Artifacts\\20878_CATufano_idiom10w_transformer+copy_wv512\\20878_CATufano_idiom10w_transformer+copy_wv512_step_35000._nb10.pred",
        "ids": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test\\abs_correct.txt",
        "src_absdir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)",
        "label_dir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt"}
    info_20878_CATufano_idiom2w={
        "pred": "G:\DDPR_backup\Artifacts\\20878_Tufano_idiom2w\\20878_Tufano_idioms2w_best_nb10.pred",
        "ids": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids",
        "src_absdir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test",
        "label_dir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test_tgt"
    }
    info_20873_Tufano_wv512_base64_copy={
        "pred": "G:\DDPR_backup\Artifacts\\20873_Tufano_wv512_base64+copy\\20873_Tufano_copy_step_100000.pred",
        "ids": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids",
        "src_absdir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test",
        "label_dir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test_tgt"
    }
    info_SR_Line={
        "ids":"D:\DDPR_DATA\OneLine_Replacement\Raw_line\\test.ids",
        "pred":"G:\DDPR_backup\Artifacts\\20878_SequenceR_Line\\20878_SequenceR_Line_step_85000_nb10.pred",
        "label":"D:\DDPR_DATA\OneLine_Replacement\Raw_line\\test.fix",
        "result_dir":"G:\DDPR_backup\Artifacts\\20878_SequenceR_Line"
    }
    info_SR_Method={
        "ids": "G:\DDPR_backup\OneLine_Replacement\SequenceR_Method\\test.sids",
        "pred": "G:\DDPR_backup\Artifacts\\20878_SequenceR_Method\\20878_SR_Method_step_125000_nb10.pred",
        "label": "G:\DDPR_backup\OneLine_Replacement\SequenceR_Method\\test.fix",
        "result_dir": "G:\DDPR_backup\Artifacts\\20878_SequenceR_Method"
    }
    info_SR_origin={
        "ids": "D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\test.sids",
        "pred": "G:\DDPR_backup\Artifacts\\20878_SequenceR_origin\\20878_SR_origin_best_b10.pred",
        "label": "D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\test.fix",
        "result_dir": "G:\DDPR_backup\Artifacts\\20878_SequenceR_origin"
    }
    info_Tufano_idiom10w_copy={
        "pred": "G:\DDPR_backup\Artifacts\\20878_Tufano_wv512_idiom10w+copy\\20878_tufano_wv512_idiom10w+copy_step_125000.pred",
        "ids": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)\\test.buggy.ids",
        "src_absdir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)",
        "label_dir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt"
    }
    info_Tufano_idiom10w={
        "pred": "G:\DDPR_backup\Artifacts\\20889_Tufano_wv512_idiom10w\\20889_tufano_wv512_idiom10w_best_b10.pred",
        "ids": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)\\test.buggy.ids",
        "src_absdir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)",
        "label_dir": "D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt"
    }
    info_CANone_transformer={
        "ids": "D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava\\test.sids",
        "pred": "G:\DDPR_backup\Artifacts\\20890_CANone_transformer_wv512\\20890_CANone_transformerwv512_best_b10.pred",
        "label": "D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava\\test.fix",
        "result_dir": "G:\DDPR_backup\Artifacts\\20890_CANone_transformer_wv512"
    }
    info_cure={
        "pred":"G:\DDPR_backup\Artifacts\\20890_cure\\new_20890_Cure_translate_nb10.pred",
        "results_dir":"G:\DDPR_backup\Artifacts\\20890_cure"
    }
    info_cure_nopretrain={
        "pred": "G:\DDPR_backup\Artifacts\\20873_Cure_nopre\\translate_nb10.pred",
        "results_dir": "G:\DDPR_backup\Artifacts\\20873_Cure_nopre"
    }
    info_CoCoNut_o2={
        "pred":"G:\DDPR_backup\Artifacts\\20878_CoCoNut_o2\\20878_CoCoNut_o2_translate_nb10.pred",
        "results_dir":"G:\DDPR_backup\Artifacts\\20878_CoCoNut_o2",
    }
    info_BPE_Tufano={
        "ids": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w\\test.ids",
        "pred": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w\\bpe2w_tufano_step_165000_nb10.pred",
        "label": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w\\test.fix.2w.bpe",
        "result_dir": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w"
    }
    info_BPE_Tufano_copy={
        "ids": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w\\test.ids",
        "pred": "G:\DDPR_backup\Artifacts\\20890_BPE_Tufano_wv512_bs64+copy_2w\\20890_BPE_Tufano_wv512_copy_step_120000.pred",
        "label": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w\\test.fix.2w.bpe",
        "result_dir": "G:\DDPR_backup\Artifacts\\20873_BPE_Tufano_2w"
    }
    #acc_Tufano(src_pred=info_20878_CATufano_idiom10w_transformer_wv512["pred"],src_ids=info_20878_CATufano_idiom10w_transformer_wv512["ids"],src_absdir=info_20878_CATufano_idiom10w_transformer_wv512["src_absdir"],label_dir=info_20878_CATufano_idiom10w_transformer_wv512['label_dir'])
    #acc_CoCoNut("G:\DDPR_backup\Artifacts\\20890_cure\\new_20890_Cure_translate_nb10.pred")
    #acc_Tufano(src_pred=info_20878_CATufano_idiom10w_transformer_wv512_copy["pred"],src_ids=info_20878_CATufano_idiom10w_transformer_wv512_copy["ids"],src_absdir=info_20878_CATufano_idiom10w_transformer_wv512_copy["src_absdir"],label_dir=info_20878_CATufano_idiom10w_transformer_wv512_copy['label_dir'])
    #acc_Tufano(src_pred=info_20878_CATufano_idiom2w["pred"],src_ids=info_20878_CATufano_idiom2w["ids"],src_absdir=info_20878_CATufano_idiom2w["src_absdir"],label_dir=info_20878_CATufano_idiom2w['label_dir'])
    #acc_Tufano(src_pred=info_20873_Tufano_wv512_base64_copy["pred"],src_ids=info_20873_Tufano_wv512_base64_copy["ids"],src_absdir=info_20873_Tufano_wv512_base64_copy["src_absdir"],label_dir=info_20873_Tufano_wv512_base64_copy['label_dir'])
    #acc_simple(ids_f=info_SR_Line["ids"],preds_f=info_SR_Line["pred"],labels_f=info_SR_Line['label'],results_dir=info_SR_Line["result_dir"])
    #acc_simple(ids_f=info_SR_Method["ids"],preds_f=info_SR_Method["pred"],labels_f=info_SR_Method['label'],results_dir=info_SR_Method["result_dir"])
    #acc_simple(ids_f=info_SR_origin["ids"],preds_f=info_SR_origin["pred"],labels_f=info_SR_origin['label'],results_dir=info_SR_origin["result_dir"])
    #acc_Tufano(src_pred=info_Tufano_idiom10w_copy["pred"],src_ids=info_Tufano_idiom10w_copy["ids"],src_absdir=info_Tufano_idiom10w_copy["src_absdir"],label_dir=info_Tufano_idiom10w_copy['label_dir'])
    #acc_Tufano(src_pred=info_Tufano_idiom10w["pred"],src_ids=info_Tufano_idiom10w["ids"],src_absdir=info_Tufano_idiom10w["src_absdir"],label_dir=info_Tufano_idiom10w['label_dir'])
    #acc_simple(ids_f=info_CANone_transformer["ids"],preds_f=info_CANone_transformer["pred"],labels_f=info_CANone_transformer['label'],results_dir=info_CANone_transformer["result_dir"])
    #acc_CoCoNut(info_cure["pred"],info_cure["results_dir"])
    #acc_CoCoNut(info_cure_nopretrain["pred"],info_cure_nopretrain["results_dir"])
    #acc_CoCoNut(info_CoCoNut_o2["pred"],info_CoCoNut_o2["results_dir"])
    #acc_simple(ids_f=info_BPE_Tufano["ids"],preds_f=info_BPE_Tufano["pred"],labels_f=info_BPE_Tufano['label'],results_dir=info_BPE_Tufano["result_dir"])
    acc_simple(ids_f=info_BPE_Tufano_copy["ids"],preds_f=info_BPE_Tufano_copy["pred"],labels_f=info_BPE_Tufano_copy['label'],results_dir=info_BPE_Tufano_copy["result_dir"])

    #acc_CoCoNut("G:\DDPR_backup\Artifacts\\20878_CoCoNut_o2\\20878_CoCoNut_o2_translate_nb10.pred")
    #analyze_mismatch("G:\DDPR_backup\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred.resultids","G:\DDPR_backup\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred.resultids2","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test_tgt","G:\DDPR_backup\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test2(map json)")