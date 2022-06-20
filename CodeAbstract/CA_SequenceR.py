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
    inputcode_f=inputcode_f.replace(".txt",".java")
    if not os.path.exists(outputcode_f):
        inputcode_f=inputcode_f.replace("bears_","").replace("bdjar_","").replace("qbs_","").replace("d4j_","")
    args=["./lib-jar/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar",inputcode_f,outputcode_f]
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

"""
add <START_BUG> before buggyline and <END_BUG> after buggyline
remove comments of code 
"""
def add_buggy_method(cont,res,max_length):
    buggy_code=res["buggy_code"]
    buggy_line=res["buggy_line"].strip()
    err_start=int(res['err_start'])
    err_end=int(res['err_end'])

    print(buggy_code[err_start])
    print(buggy_line)
    if buggy_line in buggy_code[err_start]:
        print("in")
    else:
        print("not in ")
    error_line="<START_BUG> "+buggy_line +" <END_BUG>"
    buggy_code[err_start]=error_line
    print("err_start",err_start)
    print("err_end",err_end)
    m_start_ind=0
    for ind,line in enumerate(buggy_code):
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



    buggycode=buggy_code[m_start_ind:]


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

    if hitflag==0:
        new_lines=new_lines+buggycode

        hitflag=1

    #print(new_lines)
    def remove_comments(codelines):
        pure_codes=[]
        for line in codelines:
            if str(line.strip()).startswith('/') or str(line.strip()).startswith('*'):
                continue
            else:
                pure_codes.append(line.strip())
        return pure_codes
    #print(new_lines)
    new_lines=remove_comments(new_lines)
    error_pos=new_lines.index(error_line)
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