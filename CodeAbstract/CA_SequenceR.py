import codecs
import os.path

from Utils.CA_Utils import jarWrapper

"""
implement buggy method Identify from SequenceR
code abstract at 3 levels:
    buggy line: add <START_BUG> before buggyline and <END_BUG> after buggyline
    buggy method: keep all code of the buggy method
    buggy class: keep init statement and description of other methods
"""
def run_SequenceR_abs(inputcode_f,outputcode_f,buginfo):
    args=["../lib-jar/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar",inputcode_f,outputcode_f]
    if not os.path.exists(outputcode_f):
        out,err=jarWrapper(args)
    try:
        class_content=codecs.open(outputcode_f,'r',encoding='unicode_escape').read()
        code,hitflag = add_buggy_method(class_content,buginfo)
    except:
        code=''
        hitflag=0
    return code,hitflag
def run_SequenceR_abs_p2(inputcode_f,outputcode_f,buginfo):
    args=["../lib-jar/abstraction-p2.jar",inputcode_f,outputcode_f]
    out,err=jarWrapper(args)
    err=str(err)
    try:
        class_content=codecs.open(outputcode_f,'r',encoding='unicode_escape').read()
        code,hitflag = add_buggy_method(class_content,buginfo)
    except:
        code=''
        hitflag=0
    return code,hitflag
def run_SequenceR_abs_p3(inputcode_f,outputcode_f,buginfo):
    args=["../lib-jar/abstraction-p3.jar",inputcode_f,outputcode_f]
    if not os.path.exists(outputcode_f):
        out,err=jarWrapper(args)
    try:
        class_content=codecs.open(outputcode_f,'r',encoding='unicode_escape').read()
        code,hitflag = add_buggy_method(class_content,buginfo)
    except:
        code=''
        hitflag=0
    return code,hitflag
"""
add <START_BUG> before buggyline and <END_BUG> after buggyline
remove comments of code 
"""
def add_buggy_method(cont,res):
    buggycode=res["buggy_code"].split("\n")
    err_pos=int(res['errs'][0]["src_pos"][1:-1].split(":")[0])
    if str(buggycode[0].strip()).startswith("@"):
        m_start=buggycode[1].strip().split("(")[0].strip()
        buggycode[err_pos] = "<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"
        buggy_m=buggycode[1:-2]
    else:
        m_start=buggycode[0].strip().split("(")[0].strip()
        buggycode[err_pos] = "<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"
        buggy_m = buggycode[:-2]
    buggy_m_body=[]
    for line in buggy_m:
        if line.strip().startswith("/") or line.strip().startswith("*"):
            continue
        else:
            buggy_m_body.append(line.strip())
    cont_lines=cont.split("\n")
    new_lines=[]
    hitflag=0
    for line in cont_lines:
        if line.strip().startswith("/") or line.strip().startswith("*"):
            continue
        else:
            if m_start in line:
                new_lines+=buggy_m_body
                hitflag=1
            else:
                new_lines.append(line.strip())
    return ' '.join(new_lines),hitflag
def test_run_SeqeunceR_abs():
    cp="../Example/origin/EventEmitter.java"

    outputfile="../Example/abstract/EventEmitter_SRabs.java"
    run_SequenceR_abs(cp,outputfile)
    #print(code)


