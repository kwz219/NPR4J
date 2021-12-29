import os
import argparse
import sentencepiece as spm
import yaml


def build_vocab_ONMT(config_file,clearML):
    cmd="python OpenNMT-py-master/build_vocab.py"+" -config "+config_file+" -n_sample -1" +" -clearML "+str(clearML)
    os.system(cmd)



def build_BPE_vocabs(config_file,clearML):
    with open(config_file,'r') as f:
        config_dict=yaml.safe_load(f)
    input_file=config_dict['input']
    model_prefix=config_dict['model_prefix']
    vocab_size=int(config_dict['vocab_size'])
    spm.SentencePieceTrainer.Train(input=input_file,model_prefix=model_prefix,vocab_size=vocab_size,model_type="bpe")

def main():
    parser = argparse.ArgumentParser(
        description='build_vocab.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearML",help="record experiment by clearML",default=False)
    parser.add_argument("-framework", help="", required=True,choices=["onmt","fairseq","tokenizers","spm"],default="onmt")
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.framework=="onmt":
        build_vocab_ONMT(config_file=opt.config,clearML=opt.clearML)
    if opt.framework=="spm":
        build_BPE_vocabs(config_file=opt.config,clearML=opt.clearML)

if __name__ == "__main__":
    main()
