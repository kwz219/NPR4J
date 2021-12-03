#-*- coding : utf-8-*-
import codecs
import csv
import pymongo
import os
import difflib
def write_csv2mongo(csv_path):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BF_Methods"]
    mycol = mydb["commit"]
    errcol=mydb["buginfo"]
    commitList=[]
    dirs=os.listdir("D:\BFTest")

    with open(csv_path,'r',encoding='utf-8')as f:
        reader=csv.reader(f)
        id=1
        for row in reader:
            if row[0] in dirs:
                mycol.insert_one({"_id":row[0],"repo":row[1],"commitURL":row[2],"message":row[3]})
                print(id)
                id+=1
        f.close()

def confirm_errlines():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BF_Methods"]
    mycol = mydb["Minfo_bdjar"]
    errcol=mydb["Binfo_bdjar"]
    ind=0
    for item in mycol.find({},no_cursor_timeout = True):
        bug_info=build_errs(item)
        print(ind)
        if bug_info !=None:
            errcol.insert_one(bug_info)
            ind+=1

def build_errs(method):

    Bline_buggy=int(method["BLine_buggy"])-1
    Eline_buggy=method["ELine_buggy"]
    Bline_fix=method["Bline_fix"]-1
    Eline_fix=method["Eline_fix"]
    buggy_code=codecs.open(method['buggy_file'],'r',encoding='utf8').readlines()
    fix_code=codecs.open(method['fix_file'],'r',encoding='utf8').readlines()
    if len(buggy_code)==0 and len(fix_code)==0:
        return None
    buggy_code=buggy_code[Bline_buggy:Eline_buggy]
    fix_code=fix_code[Bline_fix:Eline_fix]
    status=difflib.SequenceMatcher(None,buggy_code,fix_code)
    errlist=[]
    errtypes=set()
    for tag, i1, i2, j1, j2 in status.get_opcodes():
        #print("%7s a[%d:%d] (%s) b[%d:%d] (%s)" % (tag, i1, i2, buggy_code[i1:i2], j1, j2,fix_code[j1:j2]))
        src_pos="["+str(i1)+":"+str(i2)+"]"
        tgt_pos="["+str(j1)+":"+str(j2)+"]"
        if tag!="equal":
            err={"type":tag,"src_pos":src_pos,"tgt_pos":tgt_pos,"src_content":buggy_code[i1:i2],"tgt_content":fix_code[j1:j2]}
            errlist.append(err)
            errtypes.add(tag)

    method_errs={"parent_id":method["_id"],"errs":errlist,"num_errs":len(errlist),"type_errs":" ".join(list(errtypes)),"buggy_code":"".join(buggy_code),"fix_code":"".join(fix_code)}
    #print("------------")
    return method_errs


#write_csv2mongo("E:\\bugfixing-commits.csv")
confirm_errlines()