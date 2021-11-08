import os
from collections import Counter
from subprocess import Popen, PIPE

from Utils.IOHelper import writeL2F
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
            for file in files:
                codelines=''.join(open(corpus_dir+"\\"+file,'r',encoding='utf8').readlines())
                def isIdentifier(tok):
                    return isinstance(tok,javalang.tokenizer.Identifier)
                #using javalang to tokenize java code, and only keep token with Identifier type
                toked_code=filter(isIdentifier,list(javalang.tokenizer.tokenize(codelines)))
                tmp=Counter([tok.value for tok in toked_code])
                idioms_counter+=tmp
    idioms=[idiom[0] for idiom in idioms_counter.most_common(top_n)]
    writeL2F(idioms,targerfile)

"""
execute jar file, thanks to https://stackoverflow.com/questions/7372592/python-how-can-i-execute-a-jar-file-through-a-python-script
"""
def jarWrapper(args:list):
    process = Popen(['java', '-jar']+args, stdout=PIPE, stderr=PIPE)
    ret = []
    stdout, stderr = process.communicate()
    return stdout,stderr

"""
remove comments of java source code
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
    corpus_dir="../Example/origin"
    top_n=10
    targetfile="../CodeAbstract/CA_Resource/idioms_eg.txt"
    print(genIdioms(corpus_dir,top_n,targetfile))

