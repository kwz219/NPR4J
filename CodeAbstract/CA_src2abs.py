import os.path

from Utils.CA_Utils import jarWrapper
from Utils.IOHelper import readF2L,writeL2F
"""
code abstract method for tufano18&19
replace variables,methodcalls,types with VAR_#,METHOD_#,TYPE_#
replace literals with INT_#,FLOAT_#,CHAR_#,STRING_#
"""
def run_src2abs(code_granularity,input_code_path_A,input_code_path_B,output_abstract_path_A,output_abstract_path_B,idioms_path,mode="pair"):
    if mode=='single':
        arglist=["../lib-jar/src2abs-0.1-jar-with-dependencies.jar"]+[mode,code_granularity,input_code_path_A,output_abstract_path_A,idioms_path]
    else:
        arglist=["../lib-jar/src2abs-0.1-jar-with-dependencies.jar"]+[mode,code_granularity,input_code_path_A,input_code_path_B,output_abstract_path_A,output_abstract_path_B,idioms_path]
    result=jarWrapper(arglist)
    print(result)

def test_src2abs():
    "method "
    cg="method"
    input_code_path_a="617918d51f6e65eedfb95063.buggy"
    input_code_path_b = "617918d51f6e65eedfb95063.fix"
    output_abstract_path_a=r"a.abs"
    output_abstract_path_b = r"b.abs"
    idioms_path="D:\DDPR\CodeAbstract\CA_Resource\idioms_eg.txt"
    run_src2abs(cg,input_code_path_a,input_code_path_b,output_abstract_path_a,output_abstract_path_b,idioms_path)

def run_src2abs_all(id_file,src_dir,tgt_dir,idiom_path):
    ids=readF2L(id_file)
    ind=0
    correct_ids=[]
    error_ids=[]
    for id in ids:
        input_a=src_dir+"/"+id+".buggy"
        input_b=src_dir+"/"+id+".fix"
        out_a=tgt_dir+"/"+id+"_buggy.txt.abs"
        out_b=tgt_dir+"/"+id+"_fix.txt.abs"
        if not (os.path.exists(out_a) and os.path.exists(out_b)):
            try:
                run_src2abs("method",input_a,input_b,out_a,out_b,idiom_path)
                correct_ids.append(correct_ids)
            except:
                error_ids.append(id)
        print(ind)
        ind+=1
    writeL2F(correct_ids,tgt_dir+"/abs_correct.txt")
    writeL2F(error_ids, tgt_dir + "/abs_error.txt")


def run_src2abs_all_test(id_file,src_dir,tgt_dir,idiom_path):
    ids=readF2L(id_file)
    ind=0
    correct_ids=[]
    error_ids=[]
    for id in ids:
        input_a=src_dir+"/"+id+".buggy"

        out_a=tgt_dir+"/"+id+"_buggy.txt.abs"

        if not (os.path.exists(out_a)):
            try:
                run_src2abs("method",input_a,"",out_a,"",idiom_path,mode='single')
                correct_ids.append(id)
            except:
                error_ids.append(id)
        else:
            correct_ids.append(id)

        print(ind)
        ind+=1
    print(len(correct_ids))
    writeL2F(correct_ids,tgt_dir+"/abs_correct.txt")
    writeL2F(error_ids, tgt_dir + "/abs_error.txt")
def run_src2abs_all_test_dir(input_dir,tgt_dir,idiom_path):
    files=os.listdir(input_dir)
    correct_ids = []
    error_ids = []
    for idx,file in enumerate(files):
        input_a=input_dir+'/'+file
        out_a=tgt_dir+'/'+file+"_buggy.txt.abs"
        if not (os.path.exists(out_a)):
            try:
                run_src2abs("method",input_a,"",out_a,"",idiom_path,mode='single')
                correct_ids.append(file.split(".")[0])
            except:
                error_ids.append(file.split(".")[0])
        else:
            correct_ids.append(file.split(".")[0])
        print(idx)
    print(len(correct_ids))
    writeL2F(correct_ids,tgt_dir+"/abs_correct.txt")
    writeL2F(error_ids, tgt_dir + "/abs_error.txt")
def run_src2abs_all_test_tgt(id_file,src_dir,tgt_dir,idiom_path):
    ids=readF2L(id_file)
    ind=0
    correct_ids=[]
    error_ids=[]
    for id in ids:
        input_a=src_dir+"/"+id+".fix"

        out_a=tgt_dir+"/"+id+"_fix.txt.abs"

        if not (os.path.exists(out_a)):
            try:
                run_src2abs("method",input_a,"",out_a,"",idiom_path,mode='single')
                correct_ids.append(id)
            except:
                error_ids.append(id)
        correct_ids.append(id)
        print(ind)
        ind+=1
    writeL2F(correct_ids,tgt_dir+"/abs_correct.txt")
    writeL2F(error_ids, tgt_dir + "/abs_error.txt")

#test_src2abs()
#run_src2abs_all_test_dir("F:/NPR_DATA0306/Evaluationdata/Diversity/buggy_methods","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/srcabs","D:\DDPR\CodeAbstract\CA_Resource\idioms.2w")
#run_src2abs_all_test_dir("F:/NPR_DATA0306/Evaluationdata/Diversity/fix_methods","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/tgtabs","D:\DDPR\CodeAbstract\CA_Resource\idioms.2w")

#run_src2abs_all_test("F:/NPR_DATA0306/Evaluationdata/Diversity/test.ids",)
#run_src2abs_all_test(id_file="D:\DDPR_DATA\OneLine_Replacement\Raw\\test_max1k.ids",src_dir=r"D:/DDPR_DATA/OneLine_Replacement/Raw/test",tgt_dir=r"D:/DDPR_DATA/OneLine_Replacement/Tufano_idiom10w_abs/test-utf8",idiom_path=r"D:\DDPR\CodeAbstract\CA_Resource\idioms.10w")
#run_src2abs_all("D:\DDPR_DATA\OneLine_Replacement\Raw\\trn_max1k.ids",src_dir="D:\DDPR_DATA\OneLine_Replacement\Raw\\trn",tgt_dir="D:\DDPR_DATA\OneLine_Replacement\Tufano_idiom10w_abs\\trn_class",idiom_path="D:\DDPR\CodeAbstract\CA_Resource\idioms.10w")
#run_src2abs_all_test_tgt(id_file="D:\DDPR_DATA\OneLine_Replacement\Raw\\test_max1k.ids",src_dir=r"D:/DDPR_DATA/OneLine_Replacement/Raw/test",tgt_dir=r"D:/DDPR_DATA/OneLine_Replacement/Tufano_idiom2w_abs/test_tgt",idiom_path=r"D:\DDPR\CodeAbstract\CA_Resource\idioms.2w")
#run_src2abs_all_test_dir("F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/srcabs","D:\DDPR\CodeAbstract\CA_Resource\idioms.2w")
#run_src2abs_all_test_dir("F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_methods","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/tgtabs","D:\DDPR\CodeAbstract\CA_Resource\idioms.2w")