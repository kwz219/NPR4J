import argparse
import os

import yaml

from CodeBert_ft.run2 import mainWithArgs
from PatchEdits.evaluate_model import PatchEdits_translate

from Recoder.testone_ghl import generate_fixes, generate_fixes_d4j
import time

def translate_CoCoNut(config_file,clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    use_clearml=config_dict['clearml']
    datadir=config_dict['datadir']
    modelpath=config_dict['modelpath']
    beam=config_dict['beam']
    nbest=config_dict['nbest']
    source=config_dict['source']
    target=config_dict['target']
    taskname=config_dict['taskname']
    outputfile=config_dict['outputfile']

    cmd ="python "+"fairseq/generate.py "+datadir+" --path "+modelpath+" --beam "+str(beam)+" --nbest "+str(nbest)+\
        " -s "+source+" -t "+target+" --use-context "+" -clearml "+str(use_clearml)+" -taskname "+taskname+" -outputfile "+outputfile+" --max-sentences 1"

    os.system(cmd)
def translate_Cure(config_file,clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    use_clearml=config_dict['clearml']
    datadir=config_dict['datadir']
    modelpath=config_dict['modelpath']
    beam=config_dict['beam']
    nbest=config_dict['nbest']
    source=config_dict['source']
    target=config_dict['target']
    taskname=config_dict['taskname']
    outputfile=config_dict['outputfile']
    cmd = "python " + "fairseq/generate.py " + datadir + " --path " + modelpath + " --beam " + str(
        beam) + " --nbest " + str(nbest) + \
          " -s " + source + " -t " + target +  " -clearml " + str(
        use_clearml) + " -taskname " + taskname + " -outputfile " + outputfile+ ' --task cure'
    os.system(cmd)
#support models: sequenceR,Tufano,transformer,codit
def translate_ONMT(config_file, clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    use_clearml=clearml
    model=config_dict['model']
    src=config_dict['src']
    #tgt=config_dict['tgt']
    beam_size=config_dict['beam_size']
    n_best=config_dict['n_best']
    output=config_dict['output']
    gpu=config_dict['gpu']
    batch_size=config_dict['batch_size']
    task_name=config_file.split('/')[-1].replace('.yaml','')
    max_length=config_dict['max_length']

    cmd = "python "+" OpenNMT-py-master/onmt/bin/translate.py "+" --model "+str(model)+" --src "+str(src)+" --beam_size "+str(beam_size)+\
        " --n_best "+str(n_best)+" --output "+str(output)+" --gpu "+str(gpu)+" --batch_size "+str(batch_size)+ " -clearml "+str(use_clearml)+' -taskname '+str(task_name)+\
        " --verbose --replace_unk --max_length "+str(max_length)
    if "batch_type" in config_dict.keys():
        cmd=cmd+" --batch_type "+config_dict["batch_type"]
    os.system(cmd)

def translate_Recoder(config_file,clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()

    model_path=config_dict["model_path"]
    ids_f=config_dict["ids_path"]
    bugs_dir=config_dict["input_dir"]
    search_size=int(config_dict["search_size"])
    classcontent_dir=config_dict["classcontent_dir"]
    output_dir=config_dict["output_dir"]
    valdatapkl_f=config_dict["valdatapkl_f"]
    nl_voc_f=config_dict["nl_voc_f"]
    rule_f=config_dict["rule_f"]
    code_voc_f=config_dict["code_voc_path"]
    char_voc_path=config_dict["char_voc_path"]
    rulead_path=config_dict["rulead_path"]
    NL_voc_size=int(config_dict["NL_voc_size"])
    code_voc_size=int(config_dict["code_voc_size"])
    voc_size=int(config_dict["voc_size"])
    rule_num=int(config_dict["rule_num"])
    cnum=int(config_dict["cnum"])

    if "mode" in config_dict and config_dict["mode"]=="simple_d4j":
        generate_fixes_d4j(model_path,ids_f,bugs_dir,search_size,classcontent_dir,output_dir,valdatapkl_f,nl_voc_f,rule_f,code_voc_f,char_voc_path,rulead_path,
                   NL_voc_size,code_voc_size,voc_size,rule_num,cnum)
    else:
        generate_fixes(model_path,ids_f,bugs_dir,search_size,classcontent_dir,output_dir,valdatapkl_f,nl_voc_f,rule_f,code_voc_f,char_voc_path,rulead_path,
                       NL_voc_size,code_voc_size,voc_size,rule_num,cnum)

def translate_CodeBERT_ft(config_file):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()

    eval_batch_size = config_dict["eval_batch_size"]


    model_type= config_dict["model_type"]
    model_path=config_dict["model_name_or_path"]
    test_filename = config_dict["test_filename"]
    load_model_path = config_dict["load_model_path"]
    beam_size = int(config_dict["beam_size"])
    pref_file = config_dict["pred_file"]

    mainWithArgs(gradient_accumulation_steps=1,train_batch_size=1,train_filename='',do_train=False,
                  train_steps=0,learning_rate=0,do_eval=False,eval_steps=0,test_filename=test_filename,do_test=True,
                  warmup_steps=0,max_source_length=256,max_target_length=128,beam_size=beam_size,tokenizer_name="",weight_decay=0,adam_epsilon=1e-8,
                  dev_file_name=None,eval_batch_size=eval_batch_size,config_name="",model_name_or_path=model_path,model_type=model_type,
                  output_dir='',load_model_path=load_model_path,pred_file=pref_file)
    pass

"""
def translate_PatchEdits(config_f):
    with open(config_f, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    data_path=config_dict["data_path"]
    vocab_path=config_dict["vocab_path"]
    output_f=config_dict["output_path"]
    model_path=config_dict["model_path"]
    log_path=config_dict["log_path"]
    beam_size=config_dict["beam_size"]
    PatchEdits_translate(data_path,vocab_path,output_f,beam_size,model_path,log_path)
"""
def main():
    parser = argparse.ArgumentParser(
        description='translate.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=True)
    parser.add_argument("-model", help="", required=True,choices=["CoCoNut","Cure","onmt","Recoder","SequenceR","Tufano","PatchEdits","CodeBert_ft"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    start=time.time()
    if opt.model=="onmt" or opt.model=="SequenceR" or opt.model=="Tufano":
        translate_ONMT(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="CoCoNut":
        translate_CoCoNut(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="Cure":
        translate_Cure(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="Recoder":
        translate_Recoder(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="PatchEdits":
        PatchEdits_translate(config_f=opt.config)
    elif opt.model == "CodeBert_ft":
        translate_CodeBERT_ft(opt.config)
    end=time.time()
    time_sum=end-start
    print("total_time",time_sum)
if __name__ == "__main__":
    main()