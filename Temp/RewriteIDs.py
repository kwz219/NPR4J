def writeL2F(contents:list,filepath):
    with open(filepath,'w',encoding='utf8',errors='surrogatepass')as f:
        for line in contents:
            f.write(str(line)+'\n')
        f.close()
def readF2L(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines
def rewrite_Benchmarks_IDs(input_file):
    ori_ids=readF2L(input_file)
    prefix=''
    if "d4j" in input_file:
        prefix="d4j"
    elif "bears" in input_file:
        prefix="bears"
    elif "qbs" in input_file:
        prefix="qbs"
    elif "bdj" in input_file:
        prefix="bdjar"
    new_ids=[]
    for id in ori_ids:
        new_ids.append(prefix+'_'+id)
    writeL2F(new_ids,input_file+'.new')
rewrite_Benchmarks_IDs("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bdj.ids")
rewrite_Benchmarks_IDs("/home/zhongwenkang/RawData/Evaluation/Benchmarks/bears.ids")
rewrite_Benchmarks_IDs("/home/zhongwenkang/RawData/Evaluation/Benchmarks/qbs.ids")
rewrite_Benchmarks_IDs("/home/zhongwenkang/RawData/Evaluation/Benchmarks/d4j.ids")