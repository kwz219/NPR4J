import os.path

from Utils.CA_Utils import jarWrapper
from Utils.IOHelper import readF2L,writeL2F
"""
code abstract method for tufano18&19
replace variables,methodcalls,types with VAR_#,METHOD_#,TYPE_#
replace literals with INT_#,FLOAT_#,CHAR_#,STRING_#
"""
def run_src2abs(code_granularity,input_code_path_A,input_code_path_B,output_abstract_path_A,output_abstract_path_B,idioms_path,mode="pair"):
    arglist=["lib-jar/src2abs-0.1-jar-with-dependencies.jar"]+[mode,code_granularity,input_code_path_A,input_code_path_B,output_abstract_path_A,output_abstract_path_B,idioms_path]
    result=jarWrapper(arglist)
    #print(result)

def test_src2abs():
    cg="method"
    input_code_path_a=r"D:\DDPR\Dataset\6179103e1f6e65eedfb60702_buggy.txt"
    input_code_path_b = r"D:\DDPR\Dataset\6179103e1f6e65eedfb60702_fix.txt"
    output_abstract_path_a=r"D:\DDPR\Dataset\6179103e1f6e65eedfb60702_buggy.txt.abs"
    output_abstract_path_b = r"D:\DDPR\Dataset\6179103e1f6e65eedfb60702_fix.txt.abs"
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

#run_src2abs_all(id_file="D:\DDPR\Dataset\\val_ids.txt",src_dir=r"E:\APR_data\data\raw\val",tgt_dir=r"E:\APR_data\data\Tufano\val",idiom_path=r"E:\APR_data\data\Tufano\Idioms_2w.txt")
#run_src2abs_all("D:\DDPR\Dataset\\freq50_611\\trn_ids.txt",src_dir="D:\DDPR_DATA\OneLine_Replacement\Raw\\trn",tgt_dir="E:\APR_data\data\Tufano_idiom10w\\trn",idiom_path="D:\DDPR\CodeAbstract\CA_Resource\idioms.10w")