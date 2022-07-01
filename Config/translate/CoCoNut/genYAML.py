import yaml
def gen_CoCoNut_translate():
    datadir_prefix="/home/zhongwenkang2/RawData_Processed/CoCoNut/"
    modelpath_prefix="/home/zhongwenkang2/NPR4J-Models/CoCoNut/"
    outputfile_prefix="/home/zhongwenkang2/NPR4J_Pred/CoCoNut/"

    benchmarks=["bdj","bears","qbs","d4j"]
    CoCoNut_id=["12","15","21","32","33","35","5","99","context_tune_7","context_tune_9"]
    config_dict={"clearml":False,"taskname":"CoCoNut","source":"buggy","target":"fix","beam":300,"nbest":300,"use_context":True}

    for bench in benchmarks:
        for id in CoCoNut_id:
            config_dict["datadir"]=datadir_prefix+bench
            config_dict["modelpath"]=modelpath_prefix+"CoCoNut_"+id+"_save/checkpoint_best.pt"
            config_dict["outputfile"]=outputfile_prefix+"CoCoNut_"+id+"_b300_"+bench+'.pred'
            with open("CoCoNut_"+id+"_b300_"+bench+".yaml","w",encoding='utf8')as f:
                yaml.safe_dump(data=config_dict,stream=f)
gen_CoCoNut_translate()
