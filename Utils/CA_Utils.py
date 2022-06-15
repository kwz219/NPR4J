import codecs
import os
import re
from collections import Counter
from subprocess import Popen, PIPE


import javalang.tokenizer

from Utils.IOHelper import readF2L

"""
implement Idioms-Generating method of tufano18&19 
extract most common identifiers from  java corpus
"""

def genIdioms(corpus_dir,top_n,targerfile,tokenize="javalang",byFrequency=True):
    files=os.listdir(corpus_dir)
    idioms_counter=Counter()
    if byFrequency:
        if tokenize=="javalang":
            ind=1
            for file in files:
                try:
                    def isIdentifier(tok):
                        return isinstance(tok, javalang.tokenizer.Identifier)
                    codelines=''.join(codecs.open(corpus_dir+"\\"+file,'r',encoding='utf8').readlines())
                    # using javalang to tokenize java code, and only keep token with Identifier type
                    toked_code = filter(isIdentifier, list(javalang.tokenizer.tokenize(codelines)))
                    tmp = Counter([tok.value for tok in toked_code])
                    idioms_counter += tmp
                    ind+=1
                except:
                    ind+=1
                    continue
                print(ind)
    idioms=[idiom[0] for idiom in idioms_counter.most_common(top_n)]
    writeL2F(idioms,targerfile)
def writeL2F(contents:list,filepath):
    with open(filepath,'w',encoding='utf8',errors='surrogatepass')as f:
        for line in contents:
            f.write(str(line)+'\n')
        f.close()
def build_vocabulary(lines_f,output_f):
    lines=readF2L(lines_f)
    print(len(lines))
    vocab_counter=Counter()
    for i,line in enumerate(lines):
        tmp=Counter(line.split())
        vocab_counter+=tmp
        print(i)
    vocab_ranked=[(l,k) for k,l in sorted([(j,i) for i,j in vocab_counter.items()], reverse=True)]
    with open(output_f,'w',encoding='utf8')as f:
        for line in vocab_ranked:
            f.write(line[0]+' '+str(line[1])+'\n')
        f.close()

def genIdioms_fromlines(corpus_f,top_n,targerfile,tokenize="javalang",byFrequency=True):
    try:
        f=codecs.open(corpus_f,'r',encoding='utf8').readlines()
    except:
        f=codecs.open(corpus_f,'r',encoding='unicode_escape').readlines()
    idioms_counter=Counter()
    if byFrequency:
        if tokenize=="javalang":
            ind=1
            for code in f:
                try:
                    def isIdentifier(tok):
                        return isinstance(tok, javalang.tokenizer.Identifier)

                    # using javalang to tokenize java code, and only keep token with Identifier type
                    toked_code = filter(isIdentifier, list(javalang.tokenizer.tokenize(code)))
                    tmp = Counter([tok.value for tok in toked_code])
                    idioms_counter += tmp
                    ind+=1
                except:
                    ind+=1
                    continue
                print(ind)
    idioms=[idiom[0] for idiom in idioms_counter.most_common(top_n)]
    writeL2F(idioms,targerfile)
"""
execute jar file, thanks to https://stackoverflow.com/questions/7372592/python-how-can-i-execute-a-jar-file-through-a-python-script
"""
def jarWrapper(args:list):
    process = Popen(['java', '-jar']+args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return stdout,stderr

"""
remove comments of java CoCoNut code
"""
def remove_comments(code:str):
    clean_code=re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)|(?://.*)", "", code)
    return clean_code
def test_genIdiom():
    corpus_dir="/root/zwk/DDPR_DATA/data/M1000_Tjava/trn.buggy"
    top_n=500000
    targetfile="/root/zwk/DDPR_DATA/data/M1000_Tufano/idioms.50w"
    print(genIdioms_fromlines(corpus_dir,top_n,targetfile))

#test_genIdiom()
#build_vocabulary("F:/NPR_DATA0306/CoCoNut/trn.fix","F:/NPR_DATA0306/CoCoNut/dict.fix")
