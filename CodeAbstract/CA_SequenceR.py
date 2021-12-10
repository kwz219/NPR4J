import codecs
import os.path
import re

import nltk

from Utils.CA_Utils import jarWrapper

"""
implement buggy method Identify from SequenceR
code abstract at 3 levels:
    buggy line: add <START_BUG> before buggyline and <END_BUG> after buggyline
    buggy method: keep all code of the buggy method
    buggy class: keep init statement and description of other methods
"""
def run_SequenceR_abs(inputcode_f,outputcode_f,buginfo,max_length):
    args=["../lib-jar/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar",inputcode_f,outputcode_f]
    if not os.path.exists(outputcode_f):
        out,err=jarWrapper(args)
        #print(err)
    try:
        class_content=codecs.open(outputcode_f,'r',encoding='utf8').read()
        #print("class_content readed")
        code,hitflag = add_buggy_method(class_content,buginfo,max_length)
    except:
        print("failed ",outputcode_f)
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
import javalang
def add_buggy_method(cont,res,max_length):
    buggycode=res["buggy_code"].split("\n")
    err_pos=int(res['errs'][0]["src_pos"][1:-1].split(":")[0])
    if str(buggycode[0].strip()).startswith("@"):
        m_start=buggycode[1].strip().split("(")[0].strip()
        buggycode[err_pos] = "<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"
        errorline=buggycode[err_pos]
        buggy_m=buggycode[1:-2]
    else:
        m_start=buggycode[0].strip().split("(")[0].strip()
        buggycode[err_pos] = "<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"
        errorline = buggycode[err_pos]
        buggy_m = buggycode[:-2]

    def truncate(codelist,errorpos):
        length_list=[]

        for line in codelist:
            try:
                toked = javalang.tokenizer.tokenize(line)
                length_list.append(len(toked))
                #toked_codes.append(' '.join([tok.value for tok in toked]))
            except :
                toked=re.split(r"[.,!?;(){}]", line)
                length_list.append(len(toked))
                #toked_codes.append(' '.join(toked))
        #print("tokenized")
        assert len(length_list)==len(codelist)
        if length_list[errorpos]<=max_length:
           post_left=(max_length-length_list[errorpos])//3
           pre_left=post_left*2
        else:
            return [codelist[errorpos]]
        start_pos=max(errorpos-1,0);
        pre_count=0
        while(start_pos>0 and pre_count<pre_left):
            pre_count+=length_list[start_pos]
            start_pos=start_pos-1
        #print(start_pos)
        end_pos=min(errorpos-1,len(codelist)-1);
        post_count=0
        length=len(codelist)-1
        while(end_pos<length and post_count<post_left):
            post_count+=length_list[end_pos]
            end_pos=end_pos+1
        #print(start_pos,end_pos,len((codelist)))
        return codelist[start_pos:min(end_pos+1,length+1)]
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
    error_pos=new_lines.index(errorline)

    trunc_lines=truncate(new_lines,error_pos)

    return ' '.join(trunc_lines),hitflag
def test_run_SeqeunceR_abs():
    cp="../Example/origin/EventEmitter.java"

    outputfile="../Example/abstract/EventEmitter_SRabs.java"
    run_SequenceR_abs(cp,outputfile)
    #print(code)


