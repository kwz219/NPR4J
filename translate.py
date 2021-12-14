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


def translate_ONMT(config_file, clearML):
    pass


def main():
    parser = argparse.ArgumentParser(
        description='translate.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=True)
    parser.add_argument("-model", help="", required=True,choices=["CoCoNut","fairseq","onmt"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.model=="onmt":
        translate_ONMT(config_file=opt.config,clearML=opt.clearml)
    elif opt.model=="fairseq":
        translate_CoCoNut(config_file=opt.config,clearml=opt.clearml)

if __name__ == "__main__":
    main()