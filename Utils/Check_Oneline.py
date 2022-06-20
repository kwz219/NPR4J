import os
import difflib

from Utils.CA_Utils import writeL2F
from Utils.IOHelper import readF2L


def checkif_oneline_diff(ids_f,input_dir,output_prefix):
    ids=readF2L(ids_f)
    one_ids=[]
    none_ids=[]
    for idx,id in enumerate(ids):
        buggy_method=readF2L(os.path.join(input_dir,"buggy_methods/"+id+".txt"))
        fix_method=readF2L(os.path.join(input_dir,"fix_methods/"+id+".txt"))
        status = difflib.SequenceMatcher(None, buggy_method, fix_method)
        err_count=0
        err_types=[]
        err_lines=0
        for tag, i1, i2, j1, j2 in status.get_opcodes():
            src_pos = i2-i1
            tgt_pos = j2-j1
            if tag != "equal":
                err_count+=1
                err_types.append(tag)
                err_lines=src_pos+tgt_pos
        if err_count>1 or "insert" in err_types or "delete" in err_types :
            none_ids.append(id)
        else:
            one_ids.append(id)
    print(len(one_ids))
    print(len(none_ids))
    #writeL2F(one_ids,output_prefix+"oneline.ids")
    #writeL2F(none_ids,output_prefix+"noneline.ids")

#checkif_oneline_diff("/home/zhongwenkang/RawData/Train/trn.ids","/home/zhongwenkang/RawData/Train","/home/zhongwenkang/RawData/Train/")
#checkif_oneline_diff("/home/zhongwenkang/RawData/Valid/valid.ids","/home/zhongwenkang/RawData/Valid","/home/zhongwenkang/RawData/Valid/")