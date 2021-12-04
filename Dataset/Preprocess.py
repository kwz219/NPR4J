#-*- coding : utf-8-*-
import codecs

from bson import ObjectId
from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from CodeAbstract.CA_src2abs import run_src2abs
from Utils.IOHelper import writeL2F,readF2L
import os
def preprocess(ids:list,method,input_dir,output_dir):
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
                buggy_parent_f=bug['parent_id'].split("@")[0]
                tmp_f="D:\DDPR_TEST\SR_AB\\val_tmp\\"+buggy_parent_f.split("\\")[0]+"_"+buggy_parent_f.split("\\")[-1]
                fix_code=''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()

                buggy_code,hitflag=run_SequenceR_abs(input_dir+buggy_parent_f,tmp_f,bug)
                if len(buggy_code.strip())<=1:
                    hitflag=0
                if hitflag==1:
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    correct_ids.append(bug['_id'])
                else:
                    error_ids.append(bug['_id'])
                print(ind)
                ind+=1

            writeL2F(buggy_codes,src_f)
            writeL2F(fix_codes,tgt_f)
            writeL2F(error_ids,error_f)
            writeL2F(correct_ids, correct_f)
        build(output_dir+"val.buggy",output_dir+"val.fix",output_dir+"val.fids",output_dir+"val.sids",ids)
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
        out_a2 = input_dir.replace('trn','val') + "\\" + id + "_buggy.txt.abs"
        out_b2 = input_dir.replace('trn','val') + "\\" + id + "_fix.txt.abs"
        #print(out_a)
        if os.path.exists(out_a) and os.path.exists(out_b):
            print("already exists")
            try:
                buggy_code=codecs.open(out_a,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b,'r',encoding='utf8').read()
                if buggy_code!=fix_code and 1<=len(buggy_code.split())<=max_length :
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    success_ids.append(id)
            except:
                fail_ids.append(id)
        elif os.path.exists(out_a2) and os.path.exists(out_b2):
            print("already exists")
            try:
                buggy_code=codecs.open(out_a,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b,'r',encoding='utf8').read()
                if buggy_code!=fix_code and 1<=len(buggy_code.split())<=max_length:
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
            run_src2abs("method",buggy_f,fix_f,out_a,out_b,idom_path)
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
    writeL2F(buggy_codes,output_dir+"/"+name+".buggy")
    writeL2F(fix_codes, output_dir + "/" + name + ".fix")
    writeL2F(success_ids, output_dir + "/" + name + ".sids")
    writeL2F(fail_ids, output_dir + "/" + name + ".fids")





def test_preprocess():

    val_ids=readF2L("D:\DDPR\Dataset\\freq50_611\\val_ids.txt")
    preprocess(val_ids,"SequenceR","E:\\bug-fix\\","D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")

preprocess_Tufano("D:\DDPR\Dataset\\freq50_611\\test_ids.txt","E:\APR_data\data\Tufano\\trn","D:\DDPR_DATA\OneLine_Replacement\M1000_Tufano","E:\APR_data\data\Tufano\Idioms_2w.txt","D:\DDPR_DATA\OneLine_Replacement\Raw\\test","test")