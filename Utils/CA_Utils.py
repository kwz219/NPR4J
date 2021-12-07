import codecs
import os
from collections import Counter
from subprocess import Popen, PIPE


import javalang.tokenizer


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
    code_lines=code.split('\n')
    filtered_lines=[]
    for line in code_lines:
        line=line.strip()
        if line.startswith("/") or line.startswith("*"):
            continue
        else:
            filtered_lines.append(line)
    return ' '.join(filtered_lines)


def test_genIdiom():
    corpus_dir="/root/zwk/DDPR_DATA/data/M1000_Tjava/trn.buggy"
    top_n=500000
    targetfile="/root/zwk/DDPR_DATA/data/M1000_Tufano/idioms.50w"
    print(genIdioms_fromlines(corpus_dir,top_n,targetfile))

#test_genIdiom()