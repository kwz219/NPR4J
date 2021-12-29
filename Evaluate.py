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

def acc_CoCoNut(predf,nbest=10):
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
    #writeL2F(results_perid,results_dir+"/results_perid.txt")

def hit(label,preds):
    for pred in preds:
        if label.strip()==pred.strip():
            return 1
    return 0
def acc_Tufano(src_pred,src_ids,src_absdir,label_dir,nbest=10):
    ids=readF2L(src_ids)
    preds=readF2L(src_pred)
    def get_originlabel(label_f,map_f):
        label=codecs.open(label_f,'r').read()
        map=eval(codecs.open(map_f,'r').read())
        for key in map.keys():
            abs = " " + map[key] + " "
            if abs in pred:
                label = label.replace(abs, " " + key + " ")
        return label
    def recover_from_map(preds,map_f):
        mapfile=eval(codecs.open(map_f,'r').read())
        recovery_preds=[]
        for pred in preds:
            for key in mapfile.keys():
                abs=" "+mapfile[key]+" "
                if abs in pred:
                    pred=pred.replace(abs," "+key+" ")
            recovery_preds.append(pred)
        return recovery_preds
    print(len(ids),len(preds))
    assert len(ids)*nbest==len(preds)
    results_perid=[]
    acc_count={"acc1":0,"acc5":0,"acc10":0}
    for i,id in enumerate(ids):
        #print(id)
        label_f=label_dir+"/"+id+"_fix.txt.abs"
        #print(label_f)
        map_f=label_dir+"/"+id+"_buggy.txt.abs.map"
        bug_map_f=src_absdir+"/"+id+"_buggy.txt.abs.map"
        if not os.path.exists(label_f):
            label_f=label_f.replace('test','val')
            map_f = map_f.replace('test', 'val')

        if not os.path.exists(label_f):
            label_f=label_f.replace('val','trn')
            map_f = map_f.replace('val', 'trn')

        if not os.path.exists(label_f):
            continue
        #true_label=get_originlabel(label_f,map_f)
        true_label=codecs.open(label_f,'r').read()

        pred=preds[i*nbest:i*nbest+nbest]
        #true_preds=recover_from_map(id,pred,bug_map_f)
        true_preds=pred
        acc_1=int(true_label.strip() == true_preds[0].strip())
        acc_count["acc1"]=acc_count["acc1"]+acc_1
        acc_5=int(hit(true_label,true_preds[:5]))
        acc_count["acc5"] = acc_count["acc5"] + acc_5
        acc_10=int(hit(true_label,true_preds[:10]))
        acc_count["acc10"] = acc_count["acc10"] + acc_10
        print(i,acc_count)
        results_perid.append(id+" "+str(acc_1)+" "+str(acc_5)+" "+str(acc_10))
    for key in acc_count.keys():
        acc_count[key]=acc_count[key]/(len(preds)/nbest)
    print(acc_count)

#acc_CoCoNut(r"G:\DDPR\Artifacts\\20889_CoCoNut_o9\20878_CoCoNut_o1_translate_nb10.pred")
acc_CoCoNut(r"G:\DDPR\Artifacts\20878_CoCoNut_o9\20878_CoCoNut_o1_translate_nb10.pred")
#assert 0
acc_Tufano("G:\DDPR\Artifacts\\20878_CATufano_idiom10w_transformer+copy_wv512\\20878_CATufano_idiom10w_transformer+copywv512best_b10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test","E:\APR_data\data\Tufano_idiom10w\\test")
assert 0
acc_Tufano("G:\DDPR\Artifacts\\20873_Tufano_wv512_base64+copy\\20873_Tufano_copy_step_100000.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
assert 0
acc_Tufano("G:\DDPR\Artifacts\\20878_CATufano_idiom10w_transformer_wv512\\20878_CATufano_idiom10w_transformerwv512best_b10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test\\abs_correct.txt","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\test","E:\APR_data\data\Tufano_idiom10w\\test")
assert 0
acc_Tufano("D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\20878_Tufano_idioms2w_best_nb10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
assert 0
acc_Tufano("D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\20878_Tufano_idioms2w_best_nb10.pred","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test\\test.buggy.ids","D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom2w_abs\\test","E:\APR_data\data\Tufano\\test")
assert (0)
acc_simple("D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR/test.sids",r"G:\DDPR\Artifacts\20878_SequenceR_origin\20878_SR_origin_best_b10.pred",
           "D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\test.fix",
           r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\20878_SequenceR_origin",nbest=10)
assert (0)
acc_simple("D:/DDPR_DATA/OneLine_Replacement/M1000_Tjava/test.sids",r"G:\DDPR\Artifacts\20890_CANone_transformer_wv512\20890_CANone_transformerwv512_best_b10.pred",
           "D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava\\test.fix",
           r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\\20890_CANone_transformer_wv512",nbest=10)