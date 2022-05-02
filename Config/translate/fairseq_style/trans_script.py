import yaml


def genertae_trans_scripts(models,beam_size,n_best,data_dir,source,target,outputfile="default"):
    for i,model in enumerate(models):
        configdict={"use_context":True,"clearml":False,"taskname":model}
        configdict["modelpath"]=model
        configdict["beam"]=beam_size
        configdict["nbest"]=n_best
        configdict["datadir"]=data_dir
        configdict["source"]=source
        configdict["target"]=target

        outputfile=model.replace("checkpoint_best.pt","pred.txt")
        configdict["outputfile"]=outputfile
        with open("21063_CoCoNut_"+str(i)+"_translate_bears.yaml",'w',encoding='utf8')as f:
            yaml.dump(configdict,f)
            f.close()

models=["/root/zwk/CoCoNut/CoCoNut_12_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_15_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_21_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_32_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_33_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_5_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_99_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_35_save/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_context_tune_7/checkpoint_best.pt",
        "/root/zwk/CoCoNut/CoCoNut_context_tune_9/checkpoint_best.pt"]
genertae_trans_scripts(models,100,100,"/root/zwk/CoCoNut/Beardest","ctx","fix")