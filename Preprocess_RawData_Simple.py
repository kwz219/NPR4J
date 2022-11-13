import codecs
import os
import re
import subprocess

import javalang
from tqdm import tqdm

from CodeAbstract.CA_Recoder import generate_classcontent
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
from CodeAbstract.CA_src2abs import run_src2abs
from Utils.CA_Utils import remove_comments, jarWrapper
from Utils.IOHelper import readF2L, writeL2F, readF2L_ori
from Utils._tokenize import CoCoNut_tokenize


def readLines(f):
    lines=[]
    with open(f,'r',encoding='utf8')as f:
        for line in f:
            lines.append(line)
        f.close()
    return lines
"""
ids_f: a list of bug-fix ids
input_dir: raw data dir 
output_dir: where you want to output the processed code of SequenceR
tmp_dir: when building a SequenceR-type context, you need a directory to restore temp files
"""

def preprocess_SequenceR_Buggy_Simple(ids_f,buggy_method_dir,buggy_class_dir,output_prefix,tmp_dir,jar_path):


    ids = readF2L(ids_f)
    success_ids=[]
    failed_ids=[]
    abstracted_lines=[]
    for id in ids:
        print(id)
        print("=============")

        if id.startswith("Math_66") or id.startswith("Mockito_23") or id.startswith("Time_11"):
            continue
        elif id.startswith("Lang_37"):
            toked_bug="    public static <T> T[] addAll ( T[] array1 , T... array2 ) { if ( array1 == null ) { "+\
            " return clone ( array2 ) ; } else if ( array2 == null ) {   return clone ( array1 ) ;      } "+\
            " final Class<?> type1 = array1 . getClass() . getComponentType() ; T[] joinedArray = ( T[] ) "+\
            " Array . newInstance  ( type1 , array1 . length + array2 . length ) ; System . arraycopy ( array1 , 0 , joinedArray , 0 , array1 . length ) ;"+\
                      "System . arraycopy ( array2 , 0 , joinedArray , array1 . length , array2 . length ) ; return joinedArray ; }"
            success_ids.append(id)
            abstracted_lines.append(toked_bug.strip())
            continue
        # e.g. of id: Chart_7_TimePeriodValues_43-46
        infos = id.split("_")
        err_lines = infos[3]
        err_start = -1
        err_end = -1
        if "-" in err_lines:
            start_end = err_lines.split("-")
            err_start = int(start_end[0])
            err_end = int(start_end[1])
        else:
            err_start = int(err_lines)
            err_end = int(err_lines)

        print("error line ids",err_start,err_end)
        "generate abstract file of buggy class"
        buggy_class_f = buggy_class_dir+'/'+id+'.java'
        output_f = tmp_dir+'/'+id+'.java'
        args = [jar_path, buggy_class_f, output_f]
        if not os.path.exists(output_f):
            out, err = jarWrapper(args)

        "add error label to the method"
        method_lines = readF2L(buggy_method_dir+'/'+id+'.txt')
        if err_start == err_end:
            buggy_line = method_lines[err_start]
            method_lines[err_start]= " <START_BUG> "+ method_lines[err_start] +" <END_BUG> "+'\n'
        else:
            method_lines[err_start] = " <START_BUG> "+ method_lines[err_start]
            method_lines[err_end] = method_lines[err_end]+" <END_BUG> "+'\n'
            buggy_line = method_lines[err_start:err_end+1]
        print("buggy_line",buggy_line)

        "generate 3-level abstract file"
        abstract_class=[]
        success_flag=0
        error_start_in_class=err_start
        error_end_in_class = err_end
        try:
            class_lines = readLines(output_f)

            for idx,line in enumerate(class_lines):

                check_line = method_lines[0].replace("<START_BUG>","").replace("<END_BUG>","")

                if check_line.strip() in line.strip():
                    print(idx)
                    abstract_class = class_lines[:idx]+method_lines+class_lines[idx+1:]
                    success_flag=1
                    error_start_in_class = idx+error_start_in_class
                    error_end_in_class = idx+error_end_in_class
                    break


            print(len(abstract_class))
            clean_class=[]
            ori_error_start_in_class = error_start_in_class
            ori_error_end_in_class = error_end_in_class
            #print(abstract_class)
            print("error position in class:",error_start_in_class,error_end_in_class)
            print("buggy line in class:",abstract_class[error_start_in_class].strip(),abstract_class[error_end_in_class].strip())


            for idx,line in enumerate(abstract_class):
                line4check=str(line.strip())
                if line4check.startswith("/") or line4check.startswith("*") or line4check=="" or line4check==r"*/":
                    if idx<ori_error_start_in_class:
                        error_start_in_class= error_start_in_class-1
                        error_end_in_class = error_end_in_class-1
                    elif idx >= ori_error_start_in_class and idx<=ori_error_end_in_class:
                        clean_class.append(line)
                else:
                    #print(line.strip())
                    clean_class.append(line)

            #print(clean_class)
            #print(error_start_in_class,error_end_in_class)
            print("error_line_inclean: ",clean_class[error_start_in_class].strip(),clean_class[error_end_in_class].strip())
            assert clean_class[error_start_in_class].strip()==method_lines[err_start].strip()
            assert clean_class[error_end_in_class].strip() == method_lines[err_end].strip()
            if success_flag ==1:
                print("<START_BUG>" in ' '.join(abstract_class),"<END_BUG>" in ' '.join(abstract_class))


                def truncate(class_lines,err_start,err_end,max_length=1000):
                    length_list=[]
                    for line in class_lines:
                        try:
                            toked = javalang.tokenizer.tokenize(line)
                            length_list.append(len(toked))
                            # toked_codes.append(' '.join([tok.value for tok in toked]))
                        except:
                            toked = re.split(r"[.,!?;(){}]", line)
                            length_list.append(len(toked))
                            # toked_codes.append(' '.join(toked))
                    # print("tokenized")
                    assert len(length_list) == len(class_lines)
                    length_sum = sum(length_list)
                    if length_sum <= max_length:
                        return class_lines
                    else:
                        "start to delete from the end"
                        cur_len_satisfy=False
                        end_pos=len(class_lines)
                        while end_pos > err_end:
                            total_length = sum(length_list[:end_pos])
                            if total_length <= max_length:
                                cur_len_satisfy=True
                                break
                            else:
                                end_pos=end_pos-1
                        if cur_len_satisfy:
                            return class_lines[:end_pos]
                        else:
                            start_pos=0
                            while start_pos > err_start:
                                total_len = sum(length_list[start_pos:end_pos])
                                if total_len <=max_length:
                                    return class_lines[start_pos:end_pos]
                                else:
                                    start_pos+=1
                            return class_lines[start_pos:end_pos]
                abstract_class=truncate(clean_class,error_start_in_class,error_end_in_class)
                print("<START_BUG>" in ' '.join(abstract_class), "<END_BUG>" in ' '.join(abstract_class))
            else:
                abstract_class=method_lines

            "tokenize source codes"
            try:
                toked_bug = javalang.tokenizer.tokenize(' '.join(abstract_class))
                toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                           '<START_BUG>').replace('< END_BUG >',
                                                                                                  '<END_BUG>')
            except:
                toked_bug = re.split(r"([.,!?;(){}])", ' '.join(abstract_class))
                toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace('< END_BUG >',
                                                                                                '<END_BUG>')


            if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                try:
                    toked_bug = javalang.tokenizer.tokenize(' '.join(abstract_class))
                    toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                                   '<START_BUG>').replace('< END_BUG >',
                                                                                                          '<END_BUG>')
                except:
                    toked_bug = re.split(r"([.,!?;(){}])", ' '.join(abstract_class))
                    toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace('< END_BUG >',
                                                                                                    '<END_BUG>')
                    if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                        print(id)
                        failed_ids.append(id)
                    else:
                        success_ids.append(id)
                        abstracted_lines.append(toked_bug.strip().replace('\r\n',' ').replace('\n',' '))
            else:
                success_ids.append(id)
                abstracted_lines.append(toked_bug.strip().replace('\r\n',' ').replace('\n',' '))



        except:
            try:
                toked_bug = javalang.tokenizer.tokenize(' '.join(abstract_class))
                toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                           '<START_BUG>').replace('< END_BUG >',
                                                                                                  '<END_BUG>')
            except:
                toked_bug = re.split(r"([.,!?;(){}])", ' '.join(abstract_class))
                toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace('< END_BUG >',
                                                                                                '<END_BUG>')
                if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                    failed_ids.append(id)
                    print(id)
                else:
                    success_ids.append(id)
                    abstracted_lines.append(toked_bug.strip().replace('\r\n',' ').replace('\n',' '))

    print(len(failed_ids),failed_ids)
    writeL2F(success_ids,output_prefix+"_ids.txt")
    writeL2F(abstracted_lines,output_prefix+"_buggy.txt")
preprocess_SequenceR_Buggy_Simple(ids_f=r"D:/文档/APR-Ensemble/Defects4JData/SequenceRData/ids.txt",
                                  buggy_method_dir=r"D:/文档/APR-Ensemble/Defects4JData/SequenceRData/buggy_methods",
                                  buggy_class_dir=r"D:/文档/APR-Ensemble/Defects4JData/SequenceRData/buggy_classes",
                                  output_prefix="D:/文档/APR-Ensemble/Defects4JData/SequenceRData/SR",
                                  tmp_dir=r"D:/文档/APR-Ensemble/Defects4JData/SequenceRData/abstract_class",
                                  jar_path=r"D:/NPR4J/lib-jar/abstraction-1.0-SNAPSHOT-jar-with-dependencies.jar")




def preprocess_SequenceR_fromRaw(ids_f,input_dir,output_prefix,tmp_dir):
    ids=readF2L(ids_f)

    def build(src_f, tgt_f, error_f, correct_f, ids):
        buggy_codes = []
        fix_codes = []
        error_ids = []
        correct_ids = []
        ind = 1
        in_count = 0

        small_fixes=[]
        for id in ids:
            print(id)
            buginfo = {"_id": id}
            buginfo["buggy_code"] = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
            buginfo["buggy_line"] = codecs.open(input_dir + "/buggy_lines/" + id + '.txt', 'r',
                                                encoding='utf8').read().strip()
            id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
            buginfo["err_start"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
            buginfo["err_end"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[1])

            tmp_f = tmp_dir +'/'+ id + '.txt'
            fix_code = codecs.open(input_dir + '/fix_lines/' + id + '.txt').read().strip()

            buggy_code, hitflag = run_SequenceR_abs(input_dir + "/buggy_classes/" + id + '.txt', tmp_f, buginfo,max_length=1000)

            print("hitflag", hitflag)

            if hitflag == 1:
                try:
                    toked_fix = javalang.tokenizer.tokenize(fix_code)
                    toked_fix = ' '.join([tok.value for tok in toked_fix])
                except:
                    toked_fix = re.split(r"([.,!?;(){}])", fix_code)
                    toked_fix = ' '.join(toked_fix)

                try:
                    toked_bug = javalang.tokenizer.tokenize(buggy_code)
                    toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                                   '<START_BUG>').replace('< END_BUG >',
                                                                                                          '<END_BUG>')
                except:
                    toked_bug = re.split(r"([.,!?;(){}])", buggy_code)
                    toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace('< END_BUG >',
                                                                                                    '<END_BUG>')

                if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                    method = buginfo["buggy_code"]
                    err_end=int(buginfo["err_end"])
                    err_start=int(buginfo["err_start"])
                    err_end = min(len(method) - 1, err_end)
                    print("err_start",err_start,"err_end",err_end)
                    print(len(method))
                    error_line = "<START_BUG> " + buginfo["buggy_line"] + " <END_BUG>"
                    method = method[:err_start] + [error_line] + method[err_end:]
                    method=' '.join(method)
                    if not ("<START_BUG>" in method and "<END_BUG>" in method):
                        print("not contain flags")
                    else:
                        print("contain flags-------")
                    try:
                        toked_bug = javalang.tokenizer.tokenize(method)
                        toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                                       '<START_BUG>').replace(
                            '< END_BUG >', '<END_BUG>')
                        toked_buggyline=javalang.tokenizer.tokenize(buginfo["buggy_line"])
                        toked_buggyline=' '.join([tok.value for tok in toked_buggyline])
                        if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                            if toked_bug.count(toked_buggyline)==1:
                                toked_bug=toked_bug.replace(toked_buggyline,"<START_BUG> "+toked_buggyline+" <END_BUG>")
                            else:
                                buggy_code=buggy_code.replace('\t\n','').replace('\n','')
                                toked_bug = re.split(r"([.,!?;(){}])", buggy_code)
                                toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace(
                                    '< END_BUG >', '<END_BUG>')
                        else:
                            print("1 contain flags-------")
                    except:
                        buggy_code = buggy_code.replace('\t\n', '').replace('\n', '')
                        toked_bug = re.split(r"([.,!?;(){}])", buggy_code)
                        toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace(
                            '< END_BUG >', '<END_BUG>')

                toked_bug = toked_bug.replace("<START_BUG> <START_BUG>", "<START_BUG>").replace("<END_BUG> <END_BUG>",
                                                                                                "<END_BUG>")
                if len(toked_bug) > 10:
                    toked_bug = toked_bug.replace('\t\n', '').replace('\n', '')
                    buggy_codes.append(toked_bug)
                    if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                        print("not contain flags")
                    else:
                        print("final contain")
                    if toked_fix.strip()=="" or toked_fix.strip().isspace() or len(toked_fix)<1:
                        toked_fix = "<DELETE>"
                    toked_fix = toked_fix.replace('\t\n', ' ').replace('\n', ' ')
                    if len(toked_fix) < 2:
                        small_fixes.append(id + "<sep>" + toked_fix)
                    fix_codes.append(toked_fix)
                    correct_ids.append(buginfo['_id'])
                    in_count += 1
            elif hitflag == 2:
                error_ids.append(buginfo['_id'])
                print(tmp_f)
            else:
                try:
                    toked_fix = javalang.tokenizer.tokenize(fix_code)
                    toked_fix = ' '.join([tok.value for tok in toked_fix])
                except:
                    toked_fix = re.split(r"([.,!?;(){}])", fix_code)
                    toked_fix = ' '.join(toked_fix)
                try:
                    method = buginfo["buggy_code"]
                    err_end=int(buginfo["err_end"])
                    err_start=int(buginfo["err_start"])
                    err_end=min(len(method)-1,err_end)
                    error_line = "<START_BUG> " + buginfo["buggy_line"] + " <END_BUG>"
                    method = method[:err_start] + [error_line] + method[err_end:]
                    method=' '.join(method)
                    try:
                        toked_bug = javalang.tokenizer.tokenize(method)
                        toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >',
                                                                                       '<START_BUG>').replace(
                            '< END_BUG >', '<END_BUG>')
                        toked_buggyline=javalang.tokenizer.tokenize(buginfo["buggy_line"])
                        toked_buggyline=' '.join([tok.value for tok in toked_buggyline])
                        if not ("<START_BUG>" in toked_bug and "<END_BUG>" in toked_bug):
                            if toked_bug.count(toked_buggyline)==1:
                                toked_bug=toked_bug.replace(toked_buggyline,"<START_BUG> "+toked_buggyline+" <END_BUG>")
                            else:
                                method = method.replace('\t\n', ' ').replace('\n', ' ')

                                toked_bug = re.split(r"([.,!?;(){}])", method)
                                toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace(
                                    '< END_BUG >', '<END_BUG>')
                        else:
                            print("1 contain flags-------")
                    except:
                        method = method.replace('\t\n', ' ').replace('\n', ' ')
                        toked_bug = re.split(r"([.,!?;(){}])", method)
                        toked_bug = ' '.join(toked_bug).replace('< START_BUG >', '<START_BUG>').replace(
                            '< END_BUG >', '<END_BUG>')


                    toked_bug=toked_bug.replace("<START_BUG> <START_BUG>","<START_BUG>").replace("<END_BUG> <END_BUG>","<END_BUG>")

                    if len(toked_bug)>10:
                        toked_bug = toked_bug.replace('\t\n', '').replace('\n', '')
                        buggy_codes.append(toked_bug)
                        if toked_fix.strip()=="" or toked_fix.strip().isspace() or len(toked_fix)<1:
                            toked_fix="<DELETE>"
                        toked_fix = toked_fix.replace('\t\n', ' ').replace('\n', ' ')
                        if len(toked_fix)<2:
                            small_fixes.append(id+"<sep>"+toked_fix)
                        fix_codes.append(toked_fix)

                        correct_ids.append(buginfo['_id'])
                        in_count += 1
                except:
                    continue
            print(ind, "correct:", len(correct_ids))
            print('='*20)
            ind += 1
        assert len(buggy_codes) == len(fix_codes)
        # buggy_codes,fix_codes,correct_ids=shuffle(buggy_codes,fix_codes,correct_ids)
        assert len(buggy_codes) == len(fix_codes)
        print(len(buggy_codes), len(fix_codes))
        #print(small_fixes)

        write_fail_indexs=[]

        with open("tmp.txt",'w',encoding='utf8')as f:
            for idx,line in enumerate(buggy_codes):
                try:
                    f.write(line+'\n')
                except:
                    write_fail_indexs.append(idx)
                    error_ids.append(correct_ids[idx])
            for idx,line in enumerate(fix_codes):
                try:
                    f.write(line+'\n')
                except:
                    write_fail_indexs.append(idx)
                    error_ids.append(correct_ids[idx])
            f.close()

        with open(src_f,'w',encoding='utf8')as f:
            for idx,line in enumerate(buggy_codes):
                if not idx  in write_fail_indexs:
                    f.write(line+'\n')
            f.close()
        with open(tgt_f,'w',encoding='utf8')as f:
            for idx,line in enumerate(fix_codes):
                if not idx  in write_fail_indexs:
                    f.write(line+'\n')
            f.close()
        with open(error_f,'w',encoding='utf8')as f:
            for idx,line in enumerate(list(set(error_ids))):
                f.write(line+'\n')
            f.close()
        with open(correct_f,'w',encoding='utf8')as f:
            for idx,line in enumerate(correct_ids):
                if not idx  in write_fail_indexs:
                    f.write(line+'\n')
            f.close()
        #writeL2F(buggy_codes, src_f)
        #writeL2F(fix_codes, tgt_f)
        #writeL2F(error_ids, error_f)
        #writeL2F(correct_ids, correct_f)
        # build(output_dir+"trn.buggy",output_dir+"trn.fix",output_dir+"trn.fids",output_dir+"trn.sids",ids)
    build(output_prefix+".buggy",output_prefix+".fix",output_prefix+".fids",output_prefix+".sids",ids)
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                             #"/home/zhongwenkang/RawData_Processed/SequenceR/bears","/home/zhongwenkang/RawData_Processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/d4j.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                             #"/home/zhongwenkang/RawData_Processed/SequenceR/d4j","/home/zhongwenkang/RawData_Processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                             #"/home/zhongwenkang/RawData_Processed/SequenceR/qbs","/home/zhongwenkang/RawData_Processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                             #"/home/zhongwenkang/RawData_Processed/SequenceR/bdj","/home/zhongwenkang/RawData_Processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw("/home/zhongwenkang/NPR4J_new_test/new_test/test.ids","/home/zhongwenkang/NPR4J_new_test/new_test",
                             #,"/home/zhongwenkang/NPR4J_processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw(r"E:\NPR4J\InsertionData\d4j.ids","E:/NPR4J/InsertionData",
                             #"E:/NPR4J/InsertionData_processed/SequenceR/d4j2","E:/NPR4J/InsertionData_processed/SequenceR/temp")
#preprocess_SequenceR_fromRaw(r"/home/zhongwenkang3/NPR4J_Data/BigTrain/trn.ids","/home/zhongwenkang3/NPR4J_Data/BigTrain",
                             #r"/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SR_trn","/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SR_temp")
#preprocess_SequenceR_fromRaw(r"/home/zhongwenkang3/NPR4J_Data/Small/Valid/valid.ids","/home/zhongwenkang3/NPR4J_Data/Small/Valid",
                             #r"/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/SequenceR/SR_val","/home/zhongwenkang3/RawData_Processed/SR_temp")
"""
ids_f: a list of bug-fix ids
input_dir: raw data dir 
output_dir: where you want to output the processed code of SequenceR
tmp_dir: when building a SequenceR-type context, you need a directory to restore temp files
idiom_path: tokens that will not be abstracted , eg_path: CodeAbstract/CA_Resource/Idioms.2w
mode: when you are preparing test or valid data, using mode 'test'
"""
def preprocess_Tufano_fromRaw(ids_f,input_dir,output_dir,idom_path,temp_dir,mode,max_length=1000):
    ids=readF2L(ids_f)
    buggy_codes = []
    fix_codes = []
    success_ids = []
    fail_ids = []
    ind=0
    for id in ids:
        out_a = temp_dir + "/" + id + "_buggy.txt.abs"
        out_b = temp_dir + "/" + id + "_fix.txt.abs"
        if os.path.exists(out_a) and os.path.exists(out_b):
            print("abstraction file already exists ")
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
            print("generating abstraction")
            buggy_f = input_dir + '/buggy_methods/' + id + ".txt"
            fix_f = input_dir + '/fix_methods/' + id + ".txt"

            if "test" in mode:
                run_src2abs("method",buggy_f,"",out_a,"",idom_path,mode='single')
                run_src2abs("method", fix_f, "", out_b, "", idom_path, mode='single')
            else:
                run_src2abs("method",buggy_f,fix_f,out_a,out_b,idom_path)
            if os.path.exists(out_a) and os.path.exists(out_b):
                try:
                    buggy_code = codecs.open(out_a, 'r', encoding='utf8').read()
                    fix_code = codecs.open(out_b, 'r', encoding='utf8').read()
                    if buggy_code != fix_code and 1<=len(buggy_code.split()) <= max_length:
                        buggy_codes.append(buggy_code)
                        fix_codes.append(fix_code)
                        success_ids.append(id)
                    else:
                        fail_ids.append(id)
                except:
                    fail_ids.append(id)
        print(ind,len(success_ids),len(fail_ids))
        ind+=1

    writeL2F(buggy_codes,output_dir+"/"+mode+".buggy")
    writeL2F(fix_codes, output_dir + "/" + mode + ".fix")
    writeL2F(success_ids, output_dir + "/" + mode + ".sids")
    writeL2F(fail_ids, output_dir + "/" + mode + ".fids")

#peprocess_Tufano_fromRaw(r"/home/zhongwenkang/ML/test/success.ids", "/home/zhongwenkang/ML/test",
#                              "/home/zhongwenkang/ML_Processed/Tufano",
#                              r"/home/zhongwenkang/ML_Processed/Tufano/idioms.txt",
#                              "/home/zhongwenkang/ML_Processed/Tufano/temp", "test")
#preprocess_Tufano_fromRaw(r"/home/zhongwenkang3/NPR4J_Data/BigTrain/trn.ids", "/home/zhongwenkang3/NPR4J_Data/BigTrain",
                              #"/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Tufano",
                              #r"/home/zhongwenkang3/NPR4J/CodeAbstract/CA_Resource/idioms.4w",
                              #"/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Tufano/temp", "train")
#preprocess_Tufano_fromRaw(r"/home/zhongwenkang/ML/train/success.ids","/home/zhongwenkang/ML/train","/home/zhongwenkang/ML_Processed/Tufano",
#                          r"/home/zhongwenkang/ML_Processed/Tufano/idioms.txt","/home/zhongwenkang/ML_Processed/Tufano/temp","train")
#preprocess_Tufano_fromRaw(r"/home/zhongwenkang/ML/valid/success.ids","/home/zhongwenkang/ML/valid","/home/zhongwenkang/ML_Processed/Tufano",
#                          r"/home/zhongwenkang/ML_Processed/Tufano/idioms.txt","/home/zhongwenkang/ML_Processed/Tufano/temp","valid")

#preprocess_Tufano_fromRaw("/home/zhongwenkang/NPR4J_new_test/new_test/test.ids","/home/zhongwenkang/NPR4J_new_test/new_test",
                          #"/home/zhongwenkang/NPR4J_processed/Tufano",
                          #"CodeAbstract/CA_Resource/Idioms.2w","/home/zhongwenkang/NPR4J_processed/Tufano/temp/","test")
#preprocess_Tufano_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/RawData_Processed/Tufano",
                          #"CodeAbstract/CA_Resource/Idioms.2w","/home/zhongwenkang/RawData_Processed/Tufano/temp/","bdj_test")
#preprocess_Tufano_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/RawData_Processed/Tufano",
                          #"CodeAbstract/CA_Resource/Idioms.2w","/home/zhongwenkang/RawData_Processed/Tufano/temp/","bears_test")
#preprocess_Tufano_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/d4j.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/RawData_Processed/Tufano",
                          #"CodeAbstract/CA_Resource/Idioms.2w","/home/zhongwenkang/RawData_Processed/Tufano/temp/","d4j_test")
#preprocess_Tufano_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                          #"/home/zhongwenkang/RawData_Processed/Tufano",
                          #"CodeAbstract/CA_Resource/Idioms.2w","/home/zhongwenkang/RawData_Processed/Tufano/temp/","qbs_test")
"""
ids_f: a list of bug-fix ids
input_dir: raw data dir 
output_preix: where you want to output the processed code of RewardRepair
tmp_dir: when building a SequenceR-type context, you need a directory to restore temp files
idiom_path: tokens that will not be abstracted , eg_path: CodeAbstract/CA_Resource/Idioms.2w
mode: when you are preparing test or valid data, using mode 'test'
"""
def preprocess_RewardRepair_fromRaw(ids_f,input_dir,output_prefix,tmp_dir,mode="train"):
    ids=readF2L(ids_f)
    bug_fix=[]
    error_ids = []
    correct_ids = []
    if mode == "train":
        bug_fix.append("bugid"+'\t'+"buggy"+'\t'+"patch")
        for idx,id in enumerate(ids):
            buginfo = {"_id": id}
            buginfo["buggy_code"] = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
            buginfo["buggy_line"] = codecs.open(input_dir + "/buggy_lines/" + id + '.txt', 'r',
                                                encoding='utf8').read().strip()
            id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
            buginfo["err_start"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
            buginfo["err_end"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[1])
            tmp_f = tmp_dir +'/'+ id + '.txt'
            fix_code = codecs.open(input_dir + '/fix_lines/' + id + '.txt').read().strip().replace('\t','').replace('\r\n','').replace('\n','')

            buggy_code, hitflag = run_SequenceR_abs(input_dir + "/buggy_classes/" + id + '.txt', tmp_f, buginfo,
                                                    max_length=1000)

            if len(buggy_code.strip()) <= 1:
                hitflag = 0
            print("hitflag",hitflag)
            if hitflag == 1:
                buggy_context=buggy_code.replace("<START_BUG>","").replace("<END_BUG>","").replace('\t','').replace('\r\n','').replace('\n','')
                buggy_line=codecs.open(input_dir + '/buggy_lines/' + id + '.txt').read().strip().replace('\t','').replace('\r\n','').replace('\n','')

                buggy_src="buggy: "+buggy_line+" context: "+buggy_context
                bug_fix.append(buginfo['_id']+'\t'+buggy_src+'\t'+fix_code)
                correct_ids.append(buginfo['_id'])
                print("Total,Success: ",idx, len(correct_ids))
            elif hitflag == 0:
                buggy_method=codecs.open(input_dir + '/buggy_methods/' + id + '.txt').read().strip().replace('\t','').replace('\r\n','').replace('\n','')
                buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + '.txt').read().strip().replace('\t','').replace('\r\n', '').replace('\n', '')
                buggy_src="buggy: "+buggy_line+" context: "+buggy_method
                bug_fix.append(buginfo['_id']+'\t'+buggy_src+'\t'+fix_code)
                correct_ids.append(buginfo['_id'])
                print("Total,Success: ",idx, len(correct_ids))
            elif hitflag == 2:
                error_ids.append(buginfo['_id'])
            else:
                error_ids.append(buginfo['_id'])
    elif mode == "test":
        bug_fix.append("bugid" +'\t'+"store_id"+ '\t' + "buggy" + '\t' + "patch")
        for idx, id in enumerate(ids):
            buginfo = {"_id": id}
            buginfo["buggy_code"] = readF2L_ori(input_dir + "/buggy_methods/" + id + '.txt')
            buginfo["buggy_line"] = codecs.open(input_dir + "/buggy_lines/" + id + '.txt', 'r',
                                                encoding='utf8').read().strip()
            id_metas = codecs.open(input_dir + "/metas/" + id + '.txt', 'r', encoding='utf8').read().strip()
            buginfo["err_start"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[0])
            buginfo["err_end"] = int(str(id_metas.split("<sep>")[2])[1:-1].split(":")[1])
            tmp_f = tmp_dir + '/' + id + '.txt'
            fix_code = codecs.open(input_dir + '/fix_lines/' + id + '.txt').read().strip().replace('\t', '').replace(
                '\r\n', '').replace('\n', '')

            buggy_code, hitflag = run_SequenceR_abs(input_dir + "/buggy_classes/" + id + '.txt', tmp_f, buginfo,
                                                    max_length=1000)

            if len(buggy_code.strip()) <= 1:
                hitflag = 0
            print("hitflag", hitflag)
            if hitflag == 1:
                buggy_context = buggy_code.replace("<START_BUG>", "").replace("<END_BUG>", "").replace('\t',
                                                                                                       '').replace(
                    '\r\n', '').replace('\n', '')
                buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + '.txt').read().strip().replace('\t',
                                                                                                           '').replace(
                    '\r\n', '').replace('\n', '')

                buggy_src = "buggy: " + buggy_line + " context: " + buggy_context
                bug_fix.append(str(idx)+'\t'+buginfo['_id'] + '\t' + buggy_src + '\t' + fix_code)
                correct_ids.append(buginfo['_id'])
                print("Total,Success: ", idx, len(correct_ids))
            elif hitflag == 0:
                buggy_method = codecs.open(input_dir + '/buggy_methods/' + id + '.txt').read().strip().replace('\t',
                                                                                                               '').replace(
                    '\r\n', '').replace('\n', '')
                buggy_line = codecs.open(input_dir + '/buggy_lines/' + id + '.txt').read().strip().replace('\t',
                                                                                                           '').replace(
                    '\r\n', '').replace('\n', '')
                buggy_src = "buggy: " + buggy_line + " context: " + buggy_method
                bug_fix.append(str(idx)+'\t'+buginfo['_id'] + '\t' + buggy_src + '\t' + fix_code)
                correct_ids.append(buginfo['_id'])
                print("Total,Success: ", idx, len(correct_ids))
            elif hitflag == 2:
                error_ids.append(buginfo['_id'])
            else:
                error_ids.append(buginfo['_id'])
    writeL2F(bug_fix, output_prefix + '.bug-fix.csv')
    writeL2F(error_ids, output_prefix + '.fids')
    writeL2F(correct_ids, output_prefix + '.ids')
#preprocess_RewardRepair_fromRaw("/home/zhongwenkang/RawData/Train/trn.ids","/home/zhongwenkang/RawData/Train",
                                #"/home/zhongwenkang/NPR4J_Data/RewardRepair/trn","/home/zhongwenkang/NPR4J_Data/SequenceR/temp_files")
#preprocess_RewardRepair_fromRaw("E:/NPR4J/RawData (2)/Benchmarks/d4j.ids.new","E:/NPR4J/RawData (2)/Benchmarks",
                                #"D:/RawData_Processed/RewardRepair/d4j","D:/RawData_Processed/RewardRepair/tmp","test")
#preprocess_RewardRepair_fromRaw("E:/NPR4J/RawData (2)/Benchmarks/qbs.ids.new","E:/NPR4J/RawData (2)/Benchmarks",
                                #"D:/RawData_Processed/RewardRepair/qbs","D:/RawData_Processed/RewardRepair/tmp","test")
#preprocess_RewardRepair_fromRaw("E:/NPR4J/RawData (2)/Benchmarks/bears.ids.new","E:/NPR4J/RawData (2)/Benchmarks",
                                #"D:/RawData_Processed/RewardRepair/bears","D:/RawData_Processed/RewardRepair/tmp","test")
#preprocess_RewardRepair_fromRaw("/home/zhongwenkang3/NPR4J_Data/BigTrain/trn.ids","/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed",
                                #)
def preprocess_CodeBertFT_fromRaw(ids_f,input_dir,output_prefix):
    ids=readF2L(ids_f)
    buggy_lines=[]
    fix_lines=[]
    for idx,id in enumerate(ids):
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        fix_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        buggy_lines.append(buggy_line)
        fix_lines.append(fix_line)
    writeL2F(buggy_lines,output_prefix+'.buggy')
    writeL2F(fix_lines,output_prefix+'.fix')
#preprocess_CodeBertFT_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/d4j.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                              #"/home/zhongwenkang/RawData_Processed/CodeBERT-ft/d4j")
#preprocess_CodeBertFT_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                              #"/home/zhongwenkang/RawData_Processed/CodeBERT-ft/qbs")
#preprocess_CodeBertFT_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                              #"/home/zhongwenkang/RawData_Processed/CodeBERT-ft/bears")
#preprocess_CodeBertFT_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                              #"/home/zhongwenkang/RawData_Processed/CodeBERT-ft/bdj")
def preprocess_CodeBertFT_fromRaw_methodLevel(ids_f,input_dir,output_prefix):
    ids=readF2L(ids_f)
    print(len(ids))
    buggy_methods=[]
    fix_methods=[]
    for idx,id in enumerate(ids):
        buggy_method=codecs.open(input_dir+'/buggy_methods/'+id+'.txt','r',encoding='utf8').read().strip()
        buggy_method=remove_comments(buggy_method)
        buggy_method=buggy_method.replace('\r\n','').replace('\n','').replace('\t','')
        fix_line=codecs.open(input_dir+'/fix_methods/'+id+'.txt','r',encoding='utf8').read().strip()
        fix_line=remove_comments(fix_line)
        fix_line=fix_line.replace('\r\n','').replace('\n','').replace('\t','')
        buggy_methods.append(buggy_method)
        fix_methods.append(fix_line)
        print(idx)
    writeL2F(buggy_methods,output_prefix+'.buggy')
    writeL2F(fix_methods,output_prefix+'.fix')
#preprocess_CodeBertFT_fromRaw("/home/zhongwenkang/RawData/Valid/valid.ids","/home/zhongwenkang/RawData/Valid",
#                              "/home/zhongwenkang/NPR4J_Data/CodeBertFT/val")
#preprocess_CodeBertFT_fromRaw_methodLevel("/home/zhongwenkang/ML/train/success.ids","/home/zhongwenkang/ML/train",
#                              "/home/zhongwenkang/ML_Processed/CodeBERT/train")
#preprocess_CodeBertFT_fromRaw_methodLevel("/home/zhongwenkang/ML/valid/success.ids","/home/zhongwenkang/ML/valid",
#                              "/home/zhongwenkang/ML_Processed/CodeBERT/valid")

def preprocess_Recoder_fromRaw(mode,ids_f,input_dir,output_dir):
    ids=readF2L(ids_f)
    if mode=="test":
        fail_ids=[]

        for idx,id in enumerate(ids):
            if not os.path.exists(os.path.join(output_dir,id+'.json')):
                print(idx)
                if True:
                    meta_info=codecs.open(os.path.join(input_dir,"metas",id+".txt")).read().strip()
                    filename=meta_info.split("<sep>")[-1].split('@')[0].split("\\")[-1]
                    if "BF_Rename" in filename:
                        filename=filename.split('_')[-1].replace('.buggy','.java')
                    class_path=os.path.join(input_dir,"buggy_classes",id+".java")
                    class_path=class_path.replace("d4j_","").replace("bdjar_","").replace("bears_","").replace("qbs_","")
                    generate_classcontent(class_path,os.path.join(output_dir,id+'.json')
                                          ,filename)
                '''
                except:
                    fail_ids.append(id)
                '''
        print(len(fail_ids))
        writeL2F(fail_ids,output_dir+'/fail.ids')


#preprocess_Recoder_fromRaw("test","/home/zhongwenkang/NPR4J_new_test/new_test/test.ids","/home/zhongwenkang/NPR4J_new_test/new_test",
                           #"/home/zhongwenkang/NPR4J_processed/Recoder")
#preprocess_Recoder_fromRaw("test","E:/NPR4J/RawData (2)/Benchmarks/d4j.ids.new",
                           #"E:/NPR4J/RawData (2)/Benchmarks",
                           # "D:/RawData_Processed/Recoder_d4j")
#preprocess_Recoder_fromRaw("test","/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new",
                           #"/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                            #"/home/zhongwenkang/RawData_Processed/Recoder")
#preprocess_Recoder_fromRaw("test","/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids.new",
                           #"/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                            #"/home/zhongwenkang/RawData_Processed/Recoder")
#preprocess_Recoder_fromRaw("test","/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids.new",
                           #"/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                            #"/home/zhongwenkang/RawData_Processed/Recoder")
"""
ids_f: id list
input_dir: needed buggy_methods buggy_lines fix_lines
temp_prefix: a directory which stores the processed raw data file
output_dir: a directory that stores the compressed data file (fairseq data form)
src_dict_f: dictionary for buggy codes
tgt_dict_f: dictionary for fix codes

before using , cd fairseq, run cmd 'python setup.py develop'
"""
def Preprocess_CoCoNut_fromRaw(ids_f,input_dir,temp_prefix,output_dir,src_dict_f,tgt_dict_f,mode,src_lang="buggy",tgt_lang="fix"):
    ids=readF2L(ids_f)
    buggy_codes=[]
    fix_lines=[]
    for id in ids:
        buggy_method=codecs.open(input_dir+'/buggy_methods/'+id+'.txt').read().strip()
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt').read().strip()
        fix_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt').read().strip()
        buggy_method_toked=CoCoNut_tokenize(buggy_method)
        buggy_line_toked=CoCoNut_tokenize(buggy_line)
        fix_line_toked=CoCoNut_tokenize(fix_line)
        buggy_codes.append(' '.join(buggy_line_toked)+' <CTX> '+' '.join(buggy_method_toked))
        fix_lines.append(' '.join(fix_line_toked))
    assert len(buggy_codes)==len(fix_lines)
    writeL2F(buggy_codes,temp_prefix+'.buggy')
    writeL2F(fix_lines,temp_prefix+'.fix')
    print("Tokenization completed. Now start processing......")
    if "test" in mode:
        cmd = "python fairseq/preprocess.py " + "--CoCoNut-lang " + src_lang + " --target-lang " + tgt_lang + " --workers  1" \
          + " --srcdict " + src_dict_f + " --tgtdict " + tgt_dict_f + " --testpref " + temp_prefix + " --destdir " + output_dir
        print(cmd)
        subprocess.call(cmd, shell=True)
#Preprocess_CoCoNut_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/raw_bdj_test","/home/zhongwenkang/RawData_Processed/CoCoNut/bdjar",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/dict.ctx.txt","/home/zhongwenkang/RawData_Processed/CoCoNut/dict.fix.txt","bdj_test")
#Preprocess_CoCoNut_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                           #,"/home/zhongwenkang/RawData_Processed/CoCoNut/bears",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/dict.ctx.txt","/home/zhongwenkang/RawData_Processed/CoCoNut/dict.fix.txt","bears_test")
#Preprocess_CoCoNut_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/raw_qbs_test","/home/zhongwenkang/RawData_Processed/CoCoNut/qbs",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/dict.ctx.txt","/home/zhongwenkang/RawData_Processed/CoCoNut/dict.fix.txt","qbs_test")
#Preprocess_CoCoNut_fromRaw("/home/zhongwenkang/RawData/Evaluation/Benchmarks/d4j.ids.new","/home/zhongwenkang/RawData/Evaluation/Benchmarks",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/raw_d4j_test","/home/zhongwenkang/RawData_Processed/CoCoNut/d4j",
                           #"/home/zhongwenkang/RawData_Processed/CoCoNut/dict.ctx.txt","/home/zhongwenkang/RawData_Processed/CoCoNut/dict.fix.txt","d4j_test")
#TODO: Preprocess_PatchEdits_fromRawData
def Preprocess_PatchEdits_fromSequenceR(ids_f,SequenceR_buggy_f,SequenceR_fix_f,output_data_f,output_ids_f):
    SequenceR_buggys=readF2L(SequenceR_buggy_f)
    SequenceR_fixes=readF2L(SequenceR_fix_f)
    ids=readF2L(ids_f)
    count=0
    def deal_control_char(s):
        temp = re.sub('[\x00-\x09|\x0b-\x0c|\x0e-\x1f]', '', s)
        return temp
    for i, code in enumerate(tqdm(SequenceR_buggys)):
        if not ("<START_BUG>" in code and "<END_BUG>" in code):
            continue
        fix_code = SequenceR_fixes[i].strip()
        code = deal_control_char(code)
        fix_code = deal_control_char(fix_code)
        while '###' in code:
            code = code.replace('###', '')
        while '###' in fix_code:
            fix_code = fix_code.replace('###', '')
        temp = code
        code = code.strip().split()
        start_index = code.index("<START_BUG>")
        code.remove("<START_BUG>")
        end_index = code.index("<END_BUG>")
        code.remove("<END_BUG>")
        dataset = 'test'
        data = f"{dataset} ### {' '.join(code)} ### {start_index} {end_index} ### <s> {fix_code} </s>\n"
        if data.count('###') != 3:
            print(data.count('###'), '###' in data, temp)
            print(data)
        with open(output_data_f, 'a', encoding='utf8') as fp:
            fp.write(data)

        with open(output_ids_f, 'a', encoding='utf8') as fp:
            fp.write(ids[i]+'\n')
            count += 1
    print(count)
#Preprocess_PatchEdits_fromSequenceR(r"D:\RawData_Processed\SequenceR\qbs.sids",r"D:\RawData_Processed\SequenceR\qbs.buggy",
                                    #r"D:\RawData_Processed\SequenceR\qbs.fix",r"D:\RawData_Processed\PatchEdits\qbs.data",
                                    #r"D:\RawData_Processed\PatchEdits\qbs.ids")
#Preprocess_PatchEdits_fromSequenceR(r"D:\RawData_Processed\SequenceR\bears.sids",r"D:\RawData_Processed\SequenceR\bears.buggy",
                                    #r"D:\RawData_Processed\SequenceR\bears.fix",r"D:\RawData_Processed\PatchEdits\bears.data",
                                    #r"D:\RawData_Processed\PatchEdits\bears.ids")
#Preprocess_PatchEdits_fromSequenceR(r"D:\RawData_Processed\SequenceR\bdj.sids",r"D:\RawData_Processed\SequenceR\bdj.buggy",
                                    #r"D:\RawData_Processed\SequenceR\bdj.fix",r"D:\RawData_Processed\PatchEdits\bdj.data",
                                    #r"D:\RawData_Processed\PatchEdits\bdj.ids")
#Preprocess_PatchEdits_fromSequenceR(r"D:\RawData_Processed\SequenceR\d4j.sids",r"D:\RawData_Processed\SequenceR\d4j.buggy",
                                    #r"D:\RawData_Processed\SequenceR\d4j.fix",r"D:\RawData_Processed\PatchEdits\d4j.data",
                                    #r"D:\RawData_Processed\PatchEdits\d4j.ids")

