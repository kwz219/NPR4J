from Utils.CA_Utils import jarWrapper
"""
code abstract method for tufano18&19
replace variables,methodcalls,types with VAR_#,METHOD_#,TYPE_#
replace literals with INT_#,FLOAT_#,CHAR_#,STRING_#
"""
def run_src2abs(code_granularity,input_code_path,output_abstract_path,idioms_path,mode="single"):
    arglist=["../lib-jar/src2abs-0.1-jar-with-dependencies.jar"]+[mode,code_granularity,input_code_path,output_abstract_path,idioms_path]
    result=jarWrapper(arglist)
    print(result)

def test_src2abs():
    cg="class"
    input_code_path="../Example/origin/EventEmitter.java"
    output_abstract_path="../Example/abstract/EventEmitter_src2abs.java"
    idioms_path="D:\DD_PR\CodeAbstract\CA_Resource\idioms_eg.txt"
    run_src2abs(cg,input_code_path,output_abstract_path,idioms_path)

test_src2abs()