import codecs
import os
import re

import javalang

from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from Utils.IOHelper import readF2L, writeL2F


"""
ids_f: a list of bug-fix ids
input_dir: raw data dir 
output_dir: where you want to output the processed code of SequenceR
tmp_dir: when building a SequenceR-type context, you need a directory to restore temp files
"""
def preprocess_SequenceR_fromRaw(ids_f,input_dir,output_dir,tmp_dir):
    ids=readF2L(ids_f)
    def build(src_f, tgt_f, error_f, correct_f, ids):
        buggy_codes = []
        fix_codes = []
        error_ids = []
        correct_ids=[]
        ind=1
        newline_count=0
        in_count=0
        bug_1=0
        for id in ids:
            buginfo={"_id":id}
            buginfo["buggy_code"]=codecs.open(input_dir+"/buggy_methods/"+id+'.txt','r',encoding='utf8').read().strip()
            id_metas=codecs.open(input_dir+"/metas/"+id+'.txt','r',encoding='utf8').read().strip()
            buginfo["err_pos"]=int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
            tmp_f=tmp_dir+id+'.txt'
            fix_code=codecs.open(input_dir+'/fix_lines/'+id+'.txt').read().strip()


            buggy_code,hitflag=run_SequenceR_abs(input_dir+"/buggy_classes/"+id+'.txt',tmp_f,buginfo,max_length=1000)
            print("hitflag",hitflag)
            if len(buggy_code.strip())<=1:
                    hitflag=0
            if hitflag==1:
                    try:
                        toked_fix = javalang.tokenizer.tokenize(fix_code)
                        toked_fix = ' '.join([tok.value for tok in toked_fix])
                    except:
                        toked_fix = re.split(r"([.,!?;(){}])", fix_code)
                        toked_fix = ' '.join(toked_fix)
                    try:
                        toked_bug=javalang.tokenizer.tokenize(buggy_code)
                        toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >','<START_BUG>').replace('< END_BUG >','<END_BUG>')
                    except:
                        toked_bug = re.split(r"([.,!?;(){}])", buggy_code)
                        toked_bug = ' '.join(toked_bug).replace('< START_BUG >','<START_BUG>').replace('< END_BUG >','<END_BUG>')
                    bug_count=toked_bug.count('<START_BUG>'
                    )
                    if not bug_count==1:
                        bug_1+=1
                    else:
                        buggy_codes.append(toked_bug)
                        fix_codes.append(toked_fix)
                        if '\n' in toked_bug:
                            newline_count+=1
                            print("newline_count",newline_count)
                        #print(toked_bug)
                        #print(toked_fix)
                        correct_ids.append(buginfo['_id'])
                        in_count+=1
            elif hitflag==2:
                    print(tmp_f)
            else:
                    error_ids.append(buginfo['_id'])
            print(ind,"in:",in_count,"bug >1",bug_1)
            print("newline_count", newline_count)
            ind+=1
        assert len(buggy_codes)==len(fix_codes)
            #buggy_codes,fix_codes,correct_ids=shuffle(buggy_codes,fix_codes,correct_ids)
        assert len(buggy_codes) == len(fix_codes)
        print(len(buggy_codes),len(fix_codes))
        print("newline_count", newline_count)
        writeL2F(buggy_codes,src_f)
        writeL2F(fix_codes,tgt_f)
        writeL2F(error_ids,error_f)
        writeL2F(correct_ids, correct_f)
        #build(output_dir+"trn.buggy",output_dir+"trn.fix",output_dir+"trn.fids",output_dir+"trn.sids",ids)
    build(output_dir+"trn.buggy",output_dir+"trn.fix",output_dir+"trn.fids",output_dir+"trn.sids",ids)