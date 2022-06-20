#-*- coding : utf-8-*-
import javalang
import json
import codecs
"write list to file"
def writeL2F(contents:list,filepath):
    with open(filepath,'w',encoding='utf-8',errors='surrogatepass')as f:
        for line in contents:
            #print(line)
            f.write(str(line)+'\n')
        f.close()
"read java file, using javalang tokenizer to tokenize "
def readJavaFile(filepath):
    tokens = list(javalang.tokenizer.tokenize('if(!working_dir.exists() || !working_dir.isDirectory()) {'))
    for tok in tokens:
        print(tok)
"write dict to json"
def writeD2J(contents:dict,filepath):
    jsonObj=json.dumps(contents,indent=4)
    with open(filepath,'w',encoding='utf8')as f:
        f.write(jsonObj)
        f.close()
"read file content and return a list"
def readF2L(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
def readF2L_ori(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line)
        f.close()
    return lines
def readF2L_enc(filepath,enc):
    lines=[]
    with open(filepath,'r',encoding=enc)as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
"directly write"
def write2F(content:str,filepath):
    f=codecs.open(filepath,'w',encoding='utf8')
    f.write(content)
    f.close()

