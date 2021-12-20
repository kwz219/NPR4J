import argparse
import os

import yaml


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
    use_context=config_dict['use_context']
    cmd ="python "+"fairseq/generate.py "+datadir+" --path "+modelpath+" --beam "+str(beam)+" --nbest "+str(nbest)+\
        " -s "+source+" -t "+target+" --use-context "+" -clearml "+str(use_clearml)+" -taskname "+taskname+" -outputfile "+outputfile

    os.system(cmd)


def translate_ONMT(config_file, clearml):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
        f.close()
    use_clearml=clearml
    model=config_dict['model']
    src=config_dict['src']
    tgt=config_dict['tgt']
    beam_size=config_dict['beam_size']
    n_best=config_dict['n_best']
    output=config_dict['output']
    gpu=config_dict['gpu']
    batch_size=config_dict['batch_size']
    task_name=config_file.split('/')[-1].replace('.yaml','')
    max_length=config_dict['max_length']

    cmd = "python "+" OpenNMT-py-master/onmt/bin/translate.py "+" --model "+str(model)+" --src "+str(src)+" --tgt "+str(tgt)+" --beam_size "+str(beam_size)+\
        " --n_best "+str(n_best)+" --output "+str(output)+" --gpu "+str(gpu)+" --batch_size "+str(batch_size)+ " -clearml "+str(use_clearml)+' -taskname '+str(task_name)+\
        " --verbose --replace_unk --max_length "+str(max_length)
    if "batch_type" in config_dict.keys():
        cmd=cmd+" --batch_type "+config_dict["batch_type"]
    os.system(cmd)

def main():
    parser = argparse.ArgumentParser(
        description='translate.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=True)
    parser.add_argument("-model", help="", required=True,choices=["CoCoNut","fairseq","onmt"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.model=="onmt":
        translate_ONMT(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="fairseq":
        translate_CoCoNut(config_file=opt.config,clearml=opt.clearml)

if __name__ == "__main__":
    main()