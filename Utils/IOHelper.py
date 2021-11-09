#-*- coding : utf-8-*-
import javalang
import json

"write list to file"
def writeL2F(contents:list,filepath):
    with open(filepath,'w',encoding='utf8')as f:
        for line in contents:
            f.write(str(line)+'\n')
        f.close()

def readJavaFile(filepath):
    tokens = list(javalang.tokenizer.tokenize('if(!working_dir.exists() || !working_dir.isDirectory()) {'))
    for tok in tokens:
        print(tok)

def writeD2J(contents:dict,filepath):
    jsonObj=json.dumps(contents,indent=4)
    with open(filepath,'w',encoding='utf8')as f:
        f.write(jsonObj)
        f.close()


