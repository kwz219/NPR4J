import codecs
import os.path
import re

import javalang
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
        class_content=codecs.open(outputcode_f,'r',encoding='iso8859-1').read()
        #print("class_content readed")
        code,hitflag = add_buggy_method(class_content,buginfo,max_length)
        if hitflag==3:
            print(outputcode_f)
    except:
        code=''
        hitflag=0

    return code,hitflag
def run_SequenceR_ContextM(buginfo):
    code = add_buggy_method(buginfo)
    return code
def run_SequenceR_abs_p3(inputcode_f,outputcode_f,buginfo):
    args=["../lib-jar/abstraction-p3.jar",inputcode_f,outputcode_f]
    if not os.path.exists(outputcode_f):
        out,err=jarWrapper(args)
    try:
        class_content=codecs.open(outputcode_f,'r',encoding='iso8859-1').read()
        code,hitflag = add_buggy_method(class_content,buginfo)
    except:
        code=''
        hitflag=0
    return code,hitflag
"""
add <START_BUG> before buggyline and <END_BUG> after buggyline
remove comments of code 
"""
def add_buggy_method(cont,res,max_length):
    buggycode=res["buggy_code"].split("\n")
    err_pos=int(res['errs'][0]["src_pos"][1:-1].split(":")[0])
    print("err_pos",err_pos)
    m_start_ind=0
    for ind,line in enumerate(buggycode):
        line =str(line.strip())
        if line=="":
            continue
        elif line[0].isalpha():
            m_start=line
            m_start_ind=ind
            break
        else:
            continue
    last=m_start[-1]
    postfix=m_start[-2]
    if last=="{" and (not postfix==" "):
        m_start.replace("{"," {")
    m_start=m_start.replace("final public","public final").replace("String args[]","String[] args").replace(",Appt",", Appt")
    buggycode[err_pos]="<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"
    errorline=buggycode[err_pos]

    buggycode=buggycode[m_start_ind:-2]
    #print(m_start)


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


    cont_lines=cont.split("\n")
    new_lines=[]
    hitflag=0

    for line in cont_lines:
        if m_start in line:
            new_lines+=buggycode
            hitflag=1
        else:
            new_lines.append(line.strip())
    startpos=len(new_lines)//2
    if hitflag==0:
        rep_index=new_lines.index("}",startpos)
        new_lines=new_lines[:rep_index+1]+buggycode+new_lines[rep_index+1:]

        hitflag=1


    def remove_comments(codelines):
        pure_codes=[]
        for line in codelines:
            if str(line.strip()).startswith('/') or str(line.strip()).startswith('*'):
                continue
            else:
                pure_codes.append(line.strip())
        return pure_codes
    new_lines=remove_comments(new_lines)
    error_pos=new_lines.index(errorline)
    print(error_pos)
    trunc_lines=truncate(new_lines,error_pos)

    return ' '.join(trunc_lines),hitflag

def add_buggy_method_contextM(res):
    buggycode=res["buggy_code"].split("\n")
    err_pos=int(res['errs'][0]["src_pos"][1:-1].split(":")[0])
    buggycode[err_pos]="<START_BUG> " + buggycode[err_pos].strip() + " <END_BUG>"

    def clean_data(codes):
        cleancodeline=re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)|(?://.*)","",codes)
        return cleancodeline.strip()

    codes=clean_data(' '.join(buggycode))
    return codes
def test_run_SeqeunceR_abs():
    cp="../Example/origin/EventEmitter.java"

    outputfile="../Example/abstract/EventEmitter_SRabs.java"
    run_SequenceR_abs(cp,outputfile)
    #print(code)