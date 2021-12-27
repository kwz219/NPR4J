from Utils.IOHelper import readF2L, writeL2F, readF2L_enc


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
        acc_1=int(label in pred[0])
        acc_count["acc1"]=acc_count["acc1"]+acc_1
        acc_5=int(label in pred[:5])
        acc_count["acc5"] = acc_count["acc5"] + acc_5
        acc_10=int(label in pred[:10])
        acc_count["acc10"] = acc_count["acc10"] + acc_10
        print(i,acc_count)
        results_perid.append(id+" "+str(acc_1)+" "+str(acc_5)+" "+str(acc_10))
    for key in acc_count.keys():
        acc_count[key]=acc_count[key]/len(labels)
    print(acc_count)
    writeL2F(results_perid,results_dir+"/results_perid.txt")

acc_simple("D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR/test.sids",r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\20878_SequenceR_origin\20878_SR_origin_best_b10.pred",
           "D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\test.fix",
           r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\20878_SequenceR_origin",nbest=10)
assert (0)
acc_simple("D:/DDPR_DATA/OneLine_Replacement/M1000_Tjava/test.sids",r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\20890_CANone_transformer_wv512\20890_CANone_transformerwv512_best_b10.pred",
           "D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava\\test.fix",
           r"D:\DDPR_DATA\OneLine_Replacement\Artifacts\\20890_CANone_transformer_wv512",nbest=10)