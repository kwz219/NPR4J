from Utils.IOHelper import readF2L,writeL2F

def filter_commit():
    repo_commits=readF2L("commits_inrepo.txt")
    special_repo_commits=readF2L("commits_special.txt")
    special_commits=[]
    for line in special_repo_commits:
        contents=line.strip().split("<sep>")
        num=int(contents[-1])
        if num > 50:
            special_commits+=contents[1:-2]
    print(len(repo_commits),len(special_commits))
    exclude_commits=set(repo_commits+special_commits)
    trn_ids=[]
    val_ids=[]
    with open("D:\APIMU\DD_CodeRep\Data\OneLine_Replace2.txt",'r',encoding='utf8')as f:
        for line in f:
            infos=line.split("<SEP>")
            id=infos[0]
            parent=infos[1]
            commitID=parent.split("\\")[0]
            if commitID in exclude_commits:
                val_ids.append(id)
            else:
                trn_ids.append(id)
        f.close()
    writeL2F(trn_ids,"trn_ids.txt")
    writeL2F(val_ids,"val_ids.txt")

#filter_commit()
def count_special():
    commits=readF2L("repo&commits_special.txt")
    print(len(commits))
count_special()