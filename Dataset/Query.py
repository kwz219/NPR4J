from bson import ObjectId

from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL,COMMIT_COL,Defects4j_repos,Bugs_dot_jar_repos,Bears_repos,SEP,Benchmark_repos,APR_tool_repos
from Utils.IOHelper import writeD2J, writeL2F, write2F,readF2L
import re
"""
get all information of a buggy-fix method
"""
def get_Minfo_all(M_signatures:list):
    mongoClient=MongoHelper()
    commit_col=mongoClient.get_col(COMMIT_COL)
    minfo_col=mongoClient.get_col(METHOD_COL)
    bug_col=mongoClient.get_col(BUG_COL)

    for ms in M_signatures:
        minfo=minfo_col.find_one({"_id":ms})
        buginfo=bug_col.find_one({"parent_id":ms})
        commit=minfo["commitID"]
        commitinfo=commit_col.find_one({"_id":commit})
        final_dict=refactor_buginfo(minfo,buginfo,commitinfo)
        return final_dict

"""
Organize bug information into a dict
---- _id
---- commit_info
     ---- repo
     ---- commit_url
     ---- commit_message
---- method_info
     ---- name
     ---- buggy
          --parent_file
          --start_line
          --end_line
          --code
     ---- fix
          --parent_file
          --start_line
          --end_line
          --code
---- bugfix_info
     ---- bug_nums
     ---- edit_types
     ---- bugfix_contents
          --list[errs]
            --err
              --type
              --src_pos(relative to buggy method)
              --tgt_pos(relative to  fix method)
              --src_content
              --tgt_content
"""
def refactor_buginfo(minfo:dict,buginfo:dict,commitinfo:dict):
    allinfo={}
    allinfo["id"]=minfo["_id"]
    allinfo["commit_info"]={"repo":commitinfo["repo"],
                            "commit_url:":commitinfo["commitURL"],
                            "commit_message":commitinfo["message"]}
    allinfo["method_info"]={"name":minfo["methodname"],
                            "buggy":{
                                "parent_file":minfo["buggy_file"],
                                "start_line":minfo["BLine_buggy"],
                                "end_line":minfo["ELine_buggy"],
                                "code":buginfo["buggy_code"]
                            },
                            "fix":{
                                "parent_file": minfo["fix_file"],
                                "start_line": minfo["Bline_fix"],
                                "end_line": minfo["Eline_fix"],
                                "code":buginfo["fix_code"]
                            }}
    allinfo['bugfix_info']={
        "bug_nums":buginfo["num_errs"],
        "edit_types":buginfo["type_errs"],
        "bugfix_contents":buginfo['errs']

    }
    return allinfo
"""
find commits that from repos in [Defects4j,bugs.jar,bears]
exclude these bug-fix data from training data set 
"""
def get_commits_byrepo():
    repos=set(Defects4j_repos+Bears_repos+Bugs_dot_jar_repos+Benchmark_repos+APR_tool_repos)
    all_commits=[]
    mongoClient=MongoHelper()
    commit_col=mongoClient.get_col(COMMIT_COL)
    for repo in repos:
        print(repo)
        for commit in commit_col.find({"repo":{"$regex":"/"+repo}}):
            print("find: ",commit['repo'])
            all_commits.append(commit["_id"])
    writeL2F(all_commits,"Commits_Exclude.txt")
"""
find commits whose message contains explicit bug or issue ID
"""
def get_clean_trainCommits():
    commits_exclude=readF2L("Commits_Exclude.txt")

    info_special=readF2L("commits_special.txt")
    repos_special=[]
    for info in info_special:
        info_list=info.split('<sep>')
        repos_special.append(info_list[0])

    mongoClient=MongoHelper()
    commit_col=mongoClient.get_col(COMMIT_COL)
    commits4trn=[]
    i=0

    for commit in commit_col.find():
        sha=commit['_id']
        if sha not in commits_exclude:
            repo=commit['repo']
            if repo not in repos_special:
                commits4trn.append(commit['_id'])
                print(i)
                i+=1

    writeL2F(commits4trn,"Commits4trn.txt")
def get_commits_special():
    mongoClient=MongoHelper()
    commit_col=mongoClient.get_col(COMMIT_COL)
    pattern=r".*#\d*.*"
    special_repos=set()
    for commit in commit_col.find():
        repo=commit['repo']
        message=commit['message']
        if re.match(pattern,message) :
            special_repos.add(repo)
    repo_commits_special=[]
    print("special_repos",len(special_repos))
    repo_count=1
    for repo in set(special_repos):
        repo_commit=[repo]
        count=0
        for com in commit_col.find({"repo":repo}):
            repo_commit.append(com['_id'])
            count+=1
        repo_commit.append(str(count))
        repo_commits_special.append(SEP.join(repo_commit))
        print(repo_count)
        repo_count+=1
    writeL2F(repo_commits_special,"commits_special.txt")
def test_get_Minfo_all():
    sigs=[r"0000a9af91676cde100cdff6ca8de9bda8cb272d\P_dir\src\moe\xing\databindingformatter\WriterUtil.java@private void addMethod(PsiField field)"]
    final_dict=get_Minfo_all(sigs)
    writeD2J(final_dict,"test.json")
def get_buginfos(idlist:list,bugcolname="default"):
    mongoClient=MongoHelper()
    if bugcolname=="default":
        bugcol=mongoClient.get_col(BUG_COL)
    else:
        bugcol=mongoClient.get_col(bugcolname)
    bugs=[]
    for id in idlist:
        bug=bugcol.find_one({'_id':ObjectId(id)})
        bugs.append(bug)
    return bugs

def extractContext(meta_file):
    metas=readF2L(meta_file)
    for meta in metas:
        pass


def test_get_buginfos():
    idlist=readF2L("D:\DDPR\Dataset\\trn_ids.txt")
    bugs=get_buginfos(idlist)
    target_dir="E:\APR_data\data\\raw\\trn\\"
    correct_ids=[]
    error_ids=[]
    ind=1
    for bug in bugs:
        buggy_code=bug['buggy_code']
        fix_code=bug['fix_code']
        try:
            write2F(buggy_code,target_dir+str(bug['_id'])+"_buggy.txt")
            write2F(fix_code, target_dir+str(bug['_id']) + "_fix.txt")
            correct_ids.append(str(bug['_id']))
        except:
            error_ids.append(str(bug['_id']))
        print(ind)
        ind+=1
    writeL2F(correct_ids,target_dir+"write_correct.txt")
    writeL2F(error_ids, target_dir + "write_error.txt")




#test_get_buginfos()
#get_commits_byrepo()
#get_clean_trainCommits()
