import javalang


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


