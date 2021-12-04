import codecs


def merge_data(dir,pre):
    number=["0","1","2","3","4","5","6","7"]
    postfix=["sids","fids","fix","buggy"]
    for pos in postfix:
        totallist=[]
        for n in number:
            file=dir+"/"+pre+"."+pos+"_"+n
            lines=codecs.open(file,'r',encoding='utf8').readlines()
            totallist+=lines
        output_f=dir+"/"+pre+"."+pos
        print(len(totallist))
        with open(output_f,'w',encoding='utf8')as f:
            f.writelines(totallist)
merge_data("D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR","val")
