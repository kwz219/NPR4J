import argparse

import sentencepiece as sp
import javalang
from Utils.IOHelper import readF2L, writeL2F


def tokenize_bpe(spm_model_f,src_f,out_f):
    model=sp.SentencePieceProcessor(spm_model_f)
    src_lines=readF2L(src_f)
    toked_lines=model.encode(src_lines,out_type=str)
    final_lines=[]
    for line in toked_lines:
        final_lines.append(' '.join(line))
    writeL2F(final_lines,out_f)


if __name__ =="__main__":
    parser = argparse.ArgumentParser(
        description='tokenize',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-framework", help="", required=True,choices=["spm"])
    parser.add_argument("-type", help="", required=True,default='bpe')
    parser.add_argument("-out_f",help="",required=True)
    parser.add_argument("-src_f",help="",required=True)

    parser.add_argument("-model_f",help="",required=True)
    opt = parser.parse_args()
    if opt.framework=="spm" and opt.type=="bpe":
        tokenize_bpe(opt.model_f,opt.src_f,opt.out_f)

