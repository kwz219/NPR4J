import codecs
import os
import subprocess


from Utils.CA_Utils import writeL2F

from Utils.IOHelper import readF2L



def preprocess_Tufano(ids_f,input_dir,output_dir,idom_path,raw_dir,name,max_length=1000):
    ids=readF2L(ids_f)
    buggy_codes = []
    fix_codes = []
    success_ids = []
    fail_ids = []
    ind=0
    for id in ids:
        out_a = input_dir + "/" + id + "_buggy.txt.abs"
        out_b = input_dir + "/" + id + "_fix.txt.abs"
        out_a2 = input_dir.replace('trn','test') + "/" + id + "_buggy.txt.abs"
        out_b2 = input_dir.replace('trn','test') + "/" + id + "_fix.txt.abs"
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
            if buggy_f=="error":
                fail_ids.append(id)
                continue
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
def get_TufanoData(ids_f, input_dir, output_dir, idom_path, raw_dir, name, max_length=1000):
    preprocess_Tufano(ids_f, input_dir, output_dir, idom_path, raw_dir, name)
def preprocess_CoCoNut(configdict:dict):
    src_lang=configdict['src_lang']
    tgt_lang=configdict['tgt_lang']
    train_dir=configdict['train_dir']
    valid_dir=configdict['valid_dir']
    test_dir=configdict['test_dir']
    dest_dir=configdict['dest_dir']
    cmd="python fairseq/preprocess.py "+"--CoCoNut-lang "+src_lang+" --target-lang "+tgt_lang+" --workers 10 "\
         +" --trainpref "+train_dir+" --validpref "+valid_dir+" --testpref "+test_dir+" --destdir "+dest_dir
    print(cmd)
    subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    """
    ids_f="Dataset/freq50_611/trn_ids.txt"
    idoms_f="CodeAbstract/CA_Resource/idioms.10w"
    input_dir="/root/zwk/DDPR_DATA/Tufano_i10w/trntmp"
    output_dir = "/root/zwk/DDPR_DATA/Tufano_i10w"
    raw_dir="/root/zwk/DDPR_DATA/trn"
    name="trn"
    val_ids="Dataset/freq50_611/trn_ids.txt"
    val_dir = "/root/zwk/DDPR_DATA/val"
    val_ouy = "/root/zwk/DDPR_DATA/Tufano_i10w/valtmp"
    #preprocess_Tufano(ids_f,input_dir,output_dir,idoms_f,raw_dir,name="trn")
    run_src2abs_all(ids_f,raw_dir,input_dir,idoms_f)
    run_src2abs_all(val_ids, val_dir, val_ouy, idoms_f)
    """
    prerocess_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\trn",
                      "valid_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\test",
                      "dest_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\dest_2"}
    prerocess_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\trn",
                      "valid_dir":r"D:\DDPR\CoCoNut\data_example\context\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\test",
                      "dest_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\dest_2"}
    preprocess_CoCoNut(prerocess_config)
