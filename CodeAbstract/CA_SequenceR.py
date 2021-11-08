from Utils.CA_Utils import jarWrapper

"""
implement buggy method Identify from SequenceR
code abstract at 3 levels:
    buggy line: add <START_BUG> before buggyline and <END_BUG> after buggyline
    buggy method: keep all code of the buggy method
    buggy class: keep init statement and description of other methods
"""
def run_SequenceR_abs(code_path,buggyline,output_file):
    args=["../lib-jar/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar",code_path,buggyline,output_file]
    result=jarWrapper(args)
    code = filter_code("D:\DD_PR\Example\\abstract\EventEmitter_SRabs.java")
    return code

"""
add <START_BUG> before buggyline and <END_BUG> after buggyline
remove comments of code 
"""
def filter_code(filepath):
    lines=open(filepath,'r',encoding='utf8').readlines()
    filtered_lines=[]
    for i in range(len(lines)):
        line=lines[i].strip()
        if r"// BUGGY LINE BELOW" in line:
            filtered_lines.append(line.replace(r"// BUGGY LINE BELOW","<START_BUG>"))
            lines[i+1]=lines[i+1]+" <END_BUG>"
        elif line.startswith("/") or line.startswith("*"):
            continue
        else:
            filtered_lines.append(line)
    return ' '.join(filtered_lines)

def test_run_SeqeunceR_abs():
    cp="../Example/origin/EventEmitter.java"
    buggline='40'
    outputfile="../Example/abstract/EventEmitter_SRabs.java"
    code=run_SequenceR_abs(cp,buggline,outputfile)
    print(code)

