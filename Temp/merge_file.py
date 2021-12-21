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
def testindex():
    list1=[0,1,1,2,3,4,5,6,7]
    list2=[2,3,4]
    def getsubindex(list,sublist):
        listr=' '.join([str(i) for i in list])
        sublistr=' '.join([str(i) for i in sublist])
        return listr.index(sublistr)//2
    start_idx=getsubindex(list1,list2)

    end_idx=start_idx+len(list2)
    print(list1[start_idx:end_idx])
testindex()
