import codecs

import javalang

from Utils.IOHelper import readF2L,writeL2F
from Query import get_buginfos
def write_IDs(bugtype):
    if bugtype=="onelineReplace":
        #1.firstly,find special commits and commits in Defects4j,Bears,Bugs.jar; bug-fix pairs from these commits should be used for validation and test, excluded from train dataset
        repo_commits = readF2L("commits_inrepo.txt")
        special_repo_commits = readF2L("commits_special.txt")
        special_commits_test = []
        special_commits_val = []
        for line in special_repo_commits:
            contents = line.strip().split("<sep>")
            num = int(contents[-1])
            if num > 50:
                special_commits_test += contents[1:-2]
            else:
                special_commits_val +=contents[1:-2]
        #print(len(repo_commits), len(special_commits))
        exclude_commits_fortest = set(repo_commits + special_commits_test)
        exclude_commits_forval = set(special_commits_val)
        print(len(exclude_commits_forval),len(exclude_commits_fortest))
        trn_ids = []
        val_ids = []
        test_ids=[]
        with open("D:\APIMU\DD_CodeRep\Data\OneLine_Replace2.txt", 'r', encoding='utf8') as f:
            for line in f:
                infos = line.split("<SEP>")
                id = infos[0]
                parent = infos[1]
                commitID = parent.split("\\")[0]
                if commitID in exclude_commits_forval:
                    val_ids.append(id)
                elif commitID in exclude_commits_fortest:
                    test_ids.append(id)
                else:
                    trn_ids.append(id)
            f.close()
        print(len(trn_ids),len(val_ids),len(test_ids))
        writeL2F(trn_ids, "./freq50_611/trn_ids.txt")
        writeL2F(val_ids, "./freq50_611/val_ids.txt")
        writeL2F(test_ids, "./freq50_611/test_ids.txt")

def write_Rawdatasets(trn_ids_f,val_ids_f,test_ids_f):
    trn_ids=readF2L(trn_ids_f)
    val_ids=readF2L(val_ids_f)
    test_ids=readF2L(test_ids_f)
    trn_bugs=get_buginfos(trn_ids)
    #val_bugs=get_buginfos(val_ids)
    #test_ids=get_buginfos(test_ids)
    def write_bugcontents(bugs,dir):
        print(len(bugs))
        metas=[]
        for bug in bugs:
            try:
                id=bug['_id']
                metas.append(str(id)+"<SEP>"+bug['parent_id'])
                buggy_code=bug['buggy_code']
                fix_code=bug['fix_code']
                buggy_file=dir+"/"+str(id)+".buggy"
                fix_file = dir + "/" + str(id) + ".fix"
                buggy_f=codecs.open(buggy_file,'w',encoding='utf8')
                fix_f=codecs.open(fix_file,'w',encoding='utf8')
                buggy_f.write(buggy_code)
                fix_f.write(fix_code)
                buggy_f.close()
                fix_f.close()
            except:
                continue
        writeL2F(metas,dir+"/meta_info.txt")
    #write_bugcontents(test_ids,"D:\DDPR_DATA\Raw\\test")
    #write_bugcontents(val_bugs, "D:\DDPR_DATA\Raw\\val")
    write_bugcontents(trn_bugs, "D:\DDPR_DATA\Raw\\trn")

def write_RawdatasetsOther(d4j_f,bears_f,bdjar_f):
    d4j_ids=readF2L(d4j_f)
    bears_ids=readF2L(bears_f)
    bdjar_ids=readF2L(bdjar_f)
    d4j_bugs=get_buginfos(d4j_ids,'Binfo_d4j')
    bears_bugs=get_buginfos(bears_ids,'Binfo_bears')
    bdjar_bugs=get_buginfos(bdjar_ids,'Binfo_bdjar')
    def write_bugcontents(bugs,dir):
        print(len(bugs))
        metas=[]
        for bug in bugs:
            try:
                id=bug['_id']
                metas.append(str(id)+"<SEP>"+bug['parent_id'])
                buggy_code=bug['buggy_code']
                fix_code=bug['fix_code']
                buggy_file=dir+"/"+str(id)+".buggy"
                fix_file = dir + "/" + str(id) + ".fix"
                buggy_f=codecs.open(buggy_file,'w',encoding='utf8')
                fix_f=codecs.open(fix_file,'w',encoding='utf8')
                buggy_f.write(buggy_code)
                fix_f.write(fix_code)
                buggy_f.close()
                fix_f.close()
            except:
                continue
        writeL2F(metas,dir+"/meta_info.txt")
    write_bugcontents(d4j_bugs,"D:\DDPR_DATA\OneLine_Replacement\Raw\\d4j")
    write_bugcontents(bears_bugs, "D:\DDPR_DATA\OneLine_Replacement\Raw\\bears")
    write_bugcontents(bdjar_bugs, "D:\DDPR_DATA\OneLine_Replacement\Raw\\bdjar")
def write_FilteredDatasetOther(dbname,inputdir,outputdir,metas_f,max_length):
    metas=readF2L(metas_f)
    def filter(subdir,metas,max_length,tokenizer="javalang"):
        buggy_codes=[]
        fix_codes=[]
        if tokenizer=="javalang":
            success_ids=[]
            failed_ids=[]
            for meta in metas:
                bugid=meta.split("<SEP>")[0]
                try:
                    bug_content=codecs.open(subdir+"/"+bugid+".buggy",'r',encoding='utf8').read()
                    fix_content=codecs.open(subdir+"/"+bugid+".fix",'r',encoding='utf8').read()
                    bug_toked=javalang.tokenizer.tokenize(bug_content)
                    fix_toked=javalang.tokenizer.tokenize(fix_content)
                    bug_toked = [tok.value for tok in bug_toked]
                    fix_toked = [tok.value for tok in fix_toked]
                    if len(bug_toked)<=max_length and len(fix_toked)<=max_length:
                        buggy_codes.append(' '.join(bug_toked))
                        fix_codes.append(' '.join(fix_toked))
                        success_ids.append(bugid)
                    else:
                        failed_ids.append(bugid)
                except:
                    failed_ids.append(bugid)
        return buggy_codes,fix_codes,success_ids,failed_ids

    bcodes, fcodes, sids, fids = filter(inputdir , metas, max_length)
    writeL2F(bcodes,outputdir+"/"+dbname+".buggy")
    writeL2F(fcodes, outputdir + "/"+dbname+".fix")
    writeL2F(sids, outputdir + "/"+dbname+".sids")
    writeL2F(fids, outputdir + "/"+dbname+".fids")
def write_FilteredDataset(inputdir,outputdir,trn_metas_f,val_metas_f,test_metas_f,max_length=1000,tokenizer="javalang",removeComment=False):
    trn_metas=readF2L(trn_metas_f)
    val_metas=readF2L(val_metas_f)
    test_metas=readF2L(test_metas_f)
    def filter(subdir,metas,max_length,tokenizer="javalang"):
        buggy_codes=[]
        fix_codes=[]
        if tokenizer=="javalang":
            success_ids=[]
            failed_ids=[]
            for meta in metas:
                bugid=meta.split("<SEP>")[0]
                try:
                    bug_content=codecs.open(subdir+"/"+bugid+".buggy",'r',encoding='utf8').read()
                    fix_content=codecs.open(subdir+"/"+bugid+".fix",'r',encoding='utf8').read()
                    bug_toked=javalang.tokenizer.tokenize(bug_content)
                    fix_toked=javalang.tokenizer.tokenize(fix_content)
                    bug_toked = [tok.value for tok in bug_toked]
                    fix_toked = [tok.value for tok in fix_toked]
                    if len(bug_toked)<=max_length and len(fix_toked)<=max_length:
                        buggy_codes.append(' '.join(bug_toked))
                        fix_codes.append(' '.join(fix_toked))
                        success_ids.append(bugid)
                    else:
                        failed_ids.append(bugid)
                except:
                    failed_ids.append(bugid)
        return buggy_codes,fix_codes,success_ids,failed_ids

    test_bcodes, test_fcodes, test_sids, test_fids = filter(inputdir+"/test",test_metas, max_length)
    val_bcodes, val_fcodes, val_sids, val_fids = filter(inputdir+"/val",val_metas, max_length)
    trn_bcodes,trn_fcodes,trn_sids,trn_fids=filter(inputdir+"/trn",trn_metas,max_length)

    writeL2F(test_bcodes,outputdir+"/test.buggy")
    writeL2F(test_fcodes, outputdir + "/test.fix")
    writeL2F(test_sids, outputdir + "/test.sids")
    writeL2F(test_fids, outputdir + "/test.fids")

    writeL2F(val_bcodes,outputdir+"/val.buggy")
    writeL2F(val_fcodes, outputdir + "/val.fix")
    writeL2F(val_sids, outputdir + "/val.sids")
    writeL2F(val_fids, outputdir + "/val.fids")

    writeL2F(trn_bcodes,outputdir+"/trn.buggy")
    writeL2F(trn_fcodes, outputdir + "/trn.fix")
    writeL2F(trn_sids, outputdir + "/trn.sids")
    writeL2F(trn_fids, outputdir + "/trn.fids")

write_FilteredDatasetOther("test_d4j","D:\DDPR_DATA\OneLine_Replacement\Raw\d4j","D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava","D:\DDPR_DATA\OneLine_Replacement\Raw\d4j\meta_info.txt",1000)
write_FilteredDatasetOther("test_bears","D:\DDPR_DATA\OneLine_Replacement\Raw\\bears","D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava","D:\DDPR_DATA\OneLine_Replacement\Raw\\bears\meta_info.txt",1000)
write_FilteredDatasetOther("test_bdjar","D:\DDPR_DATA\OneLine_Replacement\Raw\\bdjar","D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava","D:\DDPR_DATA\OneLine_Replacement\Raw\\bdjar\meta_info.txt",1000)

#write_Rawdatasets("./freq50_611/trn_ids.txt","./freq50_611/val_ids.txt","./freq50_611/test_ids.txt")
#write_RawdatasetsOther("D:\DDPR\Dataset\OR\OR_d4j.txt","D:\DDPR\Dataset\OR\OR_bears.txt","D:\DDPR\Dataset\OR\OR_bdjar.txt")
#write_FilteredDataset("D:\DDPR_DATA\OneLine_Replacement\Raw","D:\DDPR_DATA\OneLine_Replacement\M1000_Tjava","D:\DDPR_DATA\OneLine_Replacement\Raw\\trn\\meta_info.txt","D:\DDPR_DATA\OneLine_Replacement\Raw\\val\\meta_info.txt","D:\DDPR_DATA\OneLine_Replacement\Raw\\test\\meta_info.txt")