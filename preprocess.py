import argparse
import codecs
import os
import subprocess

import javalang.tokenizer

from CodeAbstract.CA_src2abs import run_src2abs, run_src2abs_all
from Utils.CA_Utils import writeL2F

from Utils.IOHelper import readF2L



def preprocess_Tufano2(buggy_dir,fix_dir,idom_path,tmp_dir,output_dir,name):
    bug_files=os.listdir(buggy_dir)
    buggy_codes = []
    fix_codes = []
    success_ids = []
    fail_ids = []
    for idx,file in enumerate(bug_files):
        buggy_f=buggy_dir+'/'+file
        fix_f=fix_dir+'/'+file
        if os.path.exists(buggy_f) and os.path.exists(fix_f):
            out_a = tmp_dir + "/" + file + "_buggy.txt.abs"
            out_b = tmp_dir + "/" + file + "_fix.txt.abs"
            # print(out_a)
            if os.path.exists(out_a) and os.path.exists(out_b):
                print("already exists ")
                try:
                    buggy_code = codecs.open(out_a, 'r', encoding='utf8').read()
                    fix_code = codecs.open(out_b, 'r', encoding='utf8').read()
                    if buggy_code != fix_code :
                        print('added')
                        buggy_codes.append(buggy_code)
                        fix_codes.append(fix_code)
                        success_ids.append(file)
                except:
                    fail_ids.append(file)
            else:
                print("generate abstraction of code")


                run_src2abs("method", buggy_f, fix_f, out_a, out_b, idom_path)
                if os.path.exists(out_a) and os.path.exists(out_b):
                    try:
                        buggy_code = codecs.open(out_a, 'r', encoding='utf8').read()
                        fix_code = codecs.open(out_b, 'r', encoding='utf8').read()
                        if buggy_code != fix_code :
                            buggy_codes.append(buggy_code)
                            fix_codes.append(fix_code)
                            success_ids.append(file)
                    except:
                        fail_ids.append(file)
        else:
            fail_ids.append(file)
    assert len(buggy_codes)==len(fix_codes) and len(buggy_codes)==len(success_ids)
    writeL2F(buggy_codes,output_dir+"/"+name+".buggy")
    writeL2F(fix_codes, output_dir + "/" + name + ".fix")
    writeL2F(success_ids, output_dir + "/" + name + ".sids")
    writeL2F(fail_ids, output_dir + "/" + name + ".fids")





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
        #print(out_a)
        if os.path.exists(out_a) and os.path.exists(out_b):
            print("already exists ")
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
    #buggy_codes,fix_codes,success_ids=shuffle(buggy_codes,fix_codes,success_ids)
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

    cmd="python fairseq/preprocess.py "+"--CoCoNut-lang "+src_lang+" --target-lang "+tgt_lang+" --workers 1 "\
         +" --trainpref "+train_dir+" --validpref "+valid_dir+" --testpref "+test_dir+" --destdir "+dest_dir
    if 'joined_dictionary' in configdict.keys():
        cmd=cmd+" --joined-dictionary "+str(configdict["joined-dictionary"])
    if "srcdict" in configdict.keys():
        cmd=cmd+" --srcdict "+str(configdict['srcdict'])
    if "tgtdict" in configdict.keys():
        cmd = cmd + " --tgtdict " + str(configdict['tgtdict'])
    print(cmd)
    subprocess.call(cmd, shell=True)
def preprocess_Cure(configdict:dict):

    src_lang=configdict['src_lang']
    tgt_lang=configdict['tgt_lang']
    train_dir=configdict['train_dir']
    valid_dir=configdict['valid_dir']
    test_dir=configdict['test_dir']
    dest_dir=configdict['dest_dir']
    cmd="python fairseq/preprocess.py "+"--CoCoNut-lang "+src_lang+" --target-lang "+tgt_lang+" --workers 1 "\
         +" --trainpref "+train_dir+" --validpref "+valid_dir+" --testpref "+test_dir+" --destdir "+dest_dir+" --use-gpt "+"microsoft/CodeGPT-small-java"
    print(cmd)
    subprocess.call(cmd, shell=True)
def preprocess_normal(dir,outputfile,checkfile):
    files=os.listdir(dir)
    toked_contents=[]
    succeed_names=[]
    for i,file in enumerate(files):
        path=dir+'/'+file
        content=codecs.open(path,'r',encoding='utf8').read()
        try:
            toked_content=[tok.value for tok in javalang.tokenizer.tokenize(content)]
            toked_contents.append(' '.join(toked_content))
            succeed_names.append(file)
        except:
            pass
        print(i)
    writeL2F(toked_contents,outputfile)
    writeL2F(succeed_names,checkfile)
def main(args):
    if args.CA_method==None:
        preprocess_normal(args.input_dir,args.output_file)

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
    preprocess_Tufano(ids_f,input_dir,output_dir,idoms_f,raw_dir,name="trn")
    #run_src2abs_all(ids_f,raw_dir,input_dir,idoms_f)
    #run_src2abs_all(val_ids, val_dir, val_ouy, idoms_f)
    
    prerocess_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\trn",
                      "valid_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\test",
                      "dest_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\dest_2"}
    prerocess_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\trn",
                      "valid_dir":r"D:\DDPR\CoCoNut\data_example\context\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\test",
                      "dest_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\dest_2"}
    #preprocess_CoCoNut(prerocess_config)
    """
    #preprocess_normal("D:\generate_data","D:\generate_data\\toked_normal.buggy","D:\generate_data\\toked_normal.name")
    #run_src2abs_all("D:\DDPR\Dataset\\freq50_611\\test_ids.txt",src_dir="D:\DDPR_DATA\OneLine_Replacement\Raw\\test",tgt_dir="E:\APR_data\data\Tufano_idiom10w\\test",idiom_path="D:\DDPR\CodeAbstract\CA_Resource\idioms.10w")
    """
    parser = argparse.ArgumentParser(
        description='preprocess.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("CA_method","--CodeAbstractMethod",help="select a code abstract method. if none, use javalang to tokenize",default=['None'],choices=['None'])
    parser.add_argument("--input_dir",help="source input dir ,contains a number of java files")
    parser.add_argument("--output_file",help="processed result file. output tokenized codes to a file ,with each code a line")
    """
    CoCoNut_config={"src_lang":"ctx","tgt_lang":"fix","train_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/trn_47500",
                      "valid_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/val",
                      "test_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/test",
                      "dest_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/processed_context"}
    process_cureconfig={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"F:\NPR_DATA0306\CoCoNut\trn",
                      "valid_dir":r"D:\DDPR_DATA\OneLine_Replacement\Cure\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\Cure\test",
                      "dest_dir":r"D:\DDPR_DATA\OneLine_Replacement\Cure\dest",
                      }
    FConv_line_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/trn",
                      "valid_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/val",
                      "test_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/test",
                      "dest_dir":r"F:\NPR_DATA0306\CoCoNut\processed_nocontext"}
    preprocess_config={"src_lang":"buggy","tgt_lang":"fix","train_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\trn",
                      "valid_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\val",
                      "test_dir":r"D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\test",
                      "dest_dir":r"/home/zhongwenkang/NPR_DATA0306/CoCoNut/processed_context"}
    preprocess_CoCoNut(CoCoNut_config)
    preprocess_CoCoNut(FConv_line_config)


