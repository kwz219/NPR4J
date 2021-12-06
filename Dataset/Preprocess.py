#-*- coding : utf-8-*-
import codecs
import re

import javalang
import nltk
from bson import ObjectId
from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from CodeAbstract.CA_src2abs import run_src2abs
from Utils.IOHelper import writeL2F,readF2L
import os
def shuffle(list1, list2, list3):
    assert len(list1) == len(list2) and len(list2) == len(list3)
    all = []
    for line1, line2, line3 in zip(list1, list2, list3):
        if len(line1.strip()) > 1 and len(line2.strip()) > 1:
            all.append(line1 + "<SEP>" + line2 + "<SEP>" + str(line3))
    import random
    random.shuffle(all)
    new_l1 = []
    new_l2 = []
    new_l3 = []
    for line in all:
        line1, line2, line3 = line.split('<SEP>')
        new_l1.append(line1)
        new_l2.append(line2)
        new_l3.append(line3)
    return new_l1, new_l2, new_l3
def preprocess_SequenceR(ids_f,method,input_dir,output_dir):
    ids=readF2L(ids_f)
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)
    if method=="SequenceR":
        def build(src_f, tgt_f, error_f, correct_f,ids):
            buggy_codes = []
            fix_codes = []
            error_ids = []
            correct_ids=[]
            ind=1
            for id in ids:
                bug=bug_col.find_one({"_id":ObjectId(id)})
                if bug==None:
                    continue
                buggy_parent_f=bug['parent_id'].split("@")[0]
                tmp_f1="D:\DDPR_TEST\SR_AB\\val_tmp\\"+buggy_parent_f.split("\\")[0]+"_"+buggy_parent_f.split("\\")[-1]
                tmp_f2 = "D:\DDPR_TEST\SR_AB\\trn_tmp\\" + buggy_parent_f.split("\\")[0] + "_" + \
                         buggy_parent_f.split("\\")[-1]
                tmp_f3 = "D:\DDPR_TEST\SR_AB\\tmp\\" + buggy_parent_f.split("\\")[0] + "_" + \
                         buggy_parent_f.split("\\")[-1]
                if os.path.exists(tmp_f1):
                    tmp_f=tmp_f1
                elif os.path.exists(tmp_f2):
                    tmp_f=tmp_f2
                elif os.path.exists(tmp_f3):
                    tmp_f=tmp_f3
                else:
                    tmp_f=tmp_f1
                fix_code=''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()


                buggy_code,hitflag=run_SequenceR_abs(input_dir+buggy_parent_f,tmp_f,bug,max_length=1000)
                print("hitflag",hitflag)
                if len(buggy_code.strip())<=1:
                    hitflag=0
                if hitflag==1:
                    try:
                        toked_fix = javalang.tokenizer.tokenize(fix_code)
                        toked_fix = ' '.join([tok.value for tok in toked_fix])
                    except:
                        toked_fix = re.split(r"[.,!?;(){}]", fix_code)
                        toked_fix = ' '.join(toked_fix)
                    try:
                        toked_bug=javalang.tokenizer.tokenize(buggy_code)
                        toked_bug = ' '.join([tok.value for tok in toked_bug])
                    except:
                        toked_bug = re.split(r"[.,!?;(){}]", buggy_code)
                        toked_bug = ' '.join(toked_bug)
                    buggy_codes.append(toked_bug)
                    fix_codes.append(toked_fix)
                    #print(toked_bug)
                    #print(toked_fix)
                    correct_ids.append(bug['_id'])
                else:
                    error_ids.append(bug['_id'])
                print(ind)
                ind+=1
            buggy_codes,fix_codes,correct_ids=shuffle(buggy_codes,fix_codes,correct_ids)
            writeL2F(buggy_codes,src_f)
            writeL2F(fix_codes,tgt_f)
            writeL2F(error_ids,error_f)
            writeL2F(correct_ids, correct_f)
        build(output_dir+"test.buggy",output_dir+"test.fix",output_dir+"test.fids",output_dir+"test.sids",ids)
        #build(output_dir+"buggy.val.txt",output_dir+"fix.val.txt",output_dir+"error_ids.val.txt",output_dir+"correct_ids.val.txt",val_ids)

def preprocess_Tufano(ids_f,input_dir,output_dir,idom_path,raw_dir,name,max_length=1000):
    ids=readF2L(ids_f)
    buggy_codes = []
    fix_codes = []
    success_ids = []
    fail_ids = []
    ind=0
    for id in ids:
        out_a = input_dir + "\\" + id + "_buggy.txt.abs"
        out_b = input_dir + "\\" + id + "_fix.txt.abs"
        out_a2 = input_dir.replace('trn','test') + "\\" + id + "_buggy.txt.abs"
        out_b2 = input_dir.replace('trn','test') + "\\" + id + "_fix.txt.abs"
        #print(out_a)
        if os.path.exists(out_a) and os.path.exists(out_b):
            print("already exists 1")
            try:
                buggy_code=codecs.open(out_a,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b,'r',encoding='utf8').read()
                if buggy_code!=fix_code and 1<=len(buggy_code.split())<=max_length :
                    print('added')
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    success_ids.append(id)
            except:
                fail_ids.append(id)
        elif os.path.exists(out_a2) and os.path.exists(out_b2):
            print("already exists 2")
            try:
                buggy_code=codecs.open(out_a2,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b2,'r',encoding='utf8').read()
                if buggy_code!=fix_code and len(buggy_code.split())<=max_length:
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    success_ids.append(id)
            except:
                fail_ids.append(id)
        else:
            print("generate abstraction of code")
            def find_f(candidate_dir):
                for dir in candidate_dir:
                    buggy_f=dir+'/'+id + "_buggy.txt"
                    fix_f=dir+'/'+id + "_fix.txt"
                    if os.path.exists(buggy_f) and os.path.exists(fix_f):
                        return buggy_f,fix_f
                return "error","error"
            buggy_f,fix_f=find_f([raw_dir])
            """
            if buggy_f=="error":
               bug = bug_col.find_one({"_id": ObjectId(id)})
               buggy_code=bug['buggy_code']
               fix_code=bug['fix_code']
               buggy_f=codecs.open(out_a,'w',encoding='utf8')
               fix_f = codecs.open(out_a, 'w', encoding='utf8')
               buggy_f.write(buggy_code)
               fix_f.write(fix_code)
               buggy_f.close()
               fix_f.close()
            """
            tmp_a=out_a.replace("trn","tmp")
            tmp_b=out_b.replace("trn","tmp")
            run_src2abs("method",buggy_f,fix_f,tmp_a,tmp_b,idom_path)
            if os.path.exists(out_a) and os.path.exists(out_b):
                try:
                    buggy_code = codecs.open(out_a, 'r', encoding='utf8').read()
                    fix_code = codecs.open(out_b, 'r', encoding='utf8').read()
                    if buggy_code != fix_code and 1<=len(buggy_code.split()) <= max_length:
                        buggy_codes.append(buggy_code)
                        fix_codes.append(fix_code)
                        success_ids.append(id)
                except:
                    fail_ids.append(id)
        print(ind)
        ind+=1

    def shuffle(list1,list2,list3):
        assert  len(list1)==len(list2) and len(list2)==len(list3)
        all=[]
        for line1,line2,line3 in zip(list1,list2,list3):
            if len(line1.strip())>1 and len(line2.strip())>1:
                all.append(line1+"<SEP>"+line2+"<SEP>"+line3)
        import random
        random.shuffle(all)
        new_l1=[]
        new_l2=[]
        new_l3=[]
        for line in all:
            line1,line2,line3=line.split('<SEP>')
            new_l1.append(line1)
            new_l2.append(line2)
            new_l3.append(line3)
        return new_l1,new_l2,new_l3
    buggy_codes,fix_codes,success_ids=shuffle(buggy_codes,fix_codes,success_ids)
    writeL2F(buggy_codes,output_dir+"/"+name+".buggy")
    writeL2F(fix_codes, output_dir + "/" + name + ".fix")
    writeL2F(success_ids, output_dir + "/" + name + ".sids")
    writeL2F(fail_ids, output_dir + "/" + name + ".fids")





def test_preprocess():

    val_ids=readF2L("D:\DDPR\Dataset\\freq50_611\\val_ids.txt")
    #preprocess(val_ids,"SequenceR","E:\\bug-fix\\","D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")


preprocess_SequenceR("D:\DDPR\Dataset\\freq50_611\\test_ids.txt","SequenceR","D:\DDPR_DATA\OneLine_Replacement\Raw\\test","D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")
#preprocess_Tufano("D:\DDPR\Dataset\\freq50_611\\val_ids.txt","E:\APR_data\data\Tufano\\trn","D:\DDPR_DATA\OneLine_Replacement\M1000_Tufano","E:\APR_data\data\Tufano\Idioms_2w.txt","D:\DDPR_DATA\OneLine_Replacement\Raw\\val","val")