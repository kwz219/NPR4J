#-*- coding : utf-8-*-
from bson import ObjectId
from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from Utils.IOHelper import writeL2F,readF2L
import os
def preprocess(trn_ids:list,val_ids:list,method,input_dir,output_dir):
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)
    if method=="SequenceR":
        def build(src_f, tgt_f, error_f, ids):
            buggy_codes = []
            fix_codes = []
            error_ids = []
            ind=1
            for id in ids:
                bug=bug_col.find_one({"_id":ObjectId(id)})
                buggy_parent_f=bug['parent_id'].split("@")[0]
                tmp_f="D:\DDPR_TEST\SR_AB\\trn_tmp\\"+buggy_parent_f.split("\\")[0]+"_"+buggy_parent_f.split("\\")[-1]
                fix_code=''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()
                #print(buggy_parent_f,tmp_f)
                buggy_code,hitflag=run_SequenceR_abs(input_dir+buggy_parent_f,tmp_f,bug)
                if hitflag==1:
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                else:
                    error_ids.append(bug['_id'])
                print(ind)
                ind+=1
            writeL2F(buggy_codes,src_f)
            writeL2F(fix_codes,tgt_f)
            writeL2F(error_ids,error_f)
        build(output_dir+"buggy.trn.txt",output_dir+"fix.trn.txt",output_dir+"error_ids.trn.txt",trn_ids)
        #build(output_dir+"buggy.val.txt",output_dir+"fix.val.txt",output_dir+"error_ids.val.txt",val_ids)

def test_preprocess():
    trn_ids=readF2L("D:\DDPR\Dataset\\trn_ids.txt")
    val_ids=readF2L("D:\DDPR\Dataset\\val_ids.txt")
    preprocess(trn_ids[150000:200000],val_ids[45000:],"SequenceR","E:\\bug-fix\\","D:\DDPR_TEST\SR_AB\\")

test_preprocess()