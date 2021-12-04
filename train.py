import os
import argparse
def train_ONMT(config_file,clearML):
    cmd="python DDPR\OpenNMT-py-master\\train.py "+"-config "+config_file +" -clearML "+str(clearML)
    os.system(cmd)

def main():
    parser = argparse.ArgumentParser(
        description='build_vocab.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearML",help="record experiment by clearML",default=True)
    parser.add_argument("-framework", help="", required=True,choices=["onmt","fairseq","None"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.framework=="onmt":
        train_ONMT(config_file=opt.config,clearML=opt.clearML)

if __name__ == "__main__":
    main()



