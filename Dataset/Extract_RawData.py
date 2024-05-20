import codecs
import json
import os.path
from shutil import copyfile


def readF2L(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line.strip())
        f.close()
    return lines

def extract_insertion_dataset(buggy_class_dir,fix_class_dir,bench,input_json,output_dir):
    buggy_infos=json.load(codecs.open(input_json,'r',encoding='utf8'))
    if not os.path.exists(output_dir+'/buggy_lines'):
        os.mkdir(output_dir + '/buggy_lines')
    if not os.path.exists(output_dir+'/buggy_methods'):
        os.mkdir(output_dir+'/buggy_methods')
    if not os.path.exists(output_dir+'/buggy_classes'):
        os.mkdir(output_dir+'/buggy_classes')
    if not os.path.exists(output_dir+'/metas'):
        os.mkdir(output_dir+'/metas')
    if not os.path.exists(output_dir+'/fix_lines'):
        os.mkdir(output_dir+'/fix_lines')
    if not os.path.exists(output_dir+'/fix_methods'):
        os.mkdir(output_dir+'/fix_methods')
    if not os.path.exists(output_dir+'/fix_classes'):
        os.mkdir(output_dir+'/fix_classes')
    ids = []
    for bug in buggy_infos:
        id=bug['_id']['$oid']
        num_errs=bug['num_errs']
        type_errs=bug['type_errs']

        metas=[]
        if int(num_errs)==1 and type_errs=="insert":
            buggy_method=bug['buggy_code']
            fix_method=bug['fix_code']
            ids.append(id)
            if bench=="qbs":
                buggy_class=bug['parent_id'].split('@')[0].split('\\')[-1]
                buggy_class_f=buggy_class_dir+'/'+buggy_class
                fix_class_f=fix_class_dir+'/'+buggy_class
                err=bug['errs'][0]
                buggy_line='\n'.join(err['src_content'])
                fix_line='\n'.join(err['tgt_content'])
                meta=("<sep>".join([id,err['src_pos'],err['tgt_pos']]))
            elif bench=='d4j':
                buggy_class=bug['parent_id'].split('@')[0].split('/')[-1]
                buggy_class_f=buggy_class_dir+'/'+buggy_class
                fix_class=buggy_class.replace('buggy','fix')
                fix_class_f=fix_class_dir+'/'+fix_class
                err=bug['errs'][0]
                buggy_line='\n'.join(err['src_content'])
                fix_line='\n'.join(err['tgt_content'])
                meta=("<sep>".join(["val",id,err['src_pos'],err['tgt_pos']]))
            elif bench=='bears':
                buggy_class_pathes=bug['parent_id'].split('@')[0].split('\\')
                #print(buggy_class_pathes)
                buggy_class='/'.join(buggy_class_pathes[3:])
                buggy_class_f=buggy_class_dir+'/'+buggy_class

                fix_class=buggy_class.replace('patch','buggy')
                fix_class_f=fix_class_dir+'/'+fix_class
                err=bug['errs'][0]
                buggy_line='\n'.join(err['src_content'])
                fix_line='\n'.join(err['tgt_content'])
                meta=("<sep>".join([id,err['src_pos'],err['tgt_pos']]))

            with open(output_dir+'/buggy_lines/'+id+'.txt','w',encoding='utf8')as f:
                f.write(buggy_line)
                f.close()

            with open(output_dir+'/fix_lines/'+id+'.txt','w',encoding='utf8')as f:
                f.write(fix_line)
                f.close()

            with open(output_dir+'/buggy_methods/'+id+'.txt','w',encoding='utf8')as f:
                f.write(buggy_method)
                f.close()

            with open(output_dir + '/fix_methods/' + id + '.txt', 'w', encoding='utf8') as f:
                f.write(fix_method)
                f.close()

            with open(output_dir + '/metas/' + id + '.txt', 'w', encoding='utf8') as f:
                f.write(meta)
                f.close()

            copyfile(buggy_class_f,output_dir+'/buggy_classes/'+id+'.java')
            copyfile(fix_class_f,output_dir+'/fix_classes/'+id+'.java')

            with open(output_dir+'/'+bench+'.ids','w',encoding='utf8')as f:
                for line in ids:
                    f.write(line+'\n')

def extract_bigdata_4train(class_dir,bench,ids_f,all_json,output_dir):
    ids=readF2L(ids_f)
    all_infos=json.load(codecs.open(all_json,'r',encoding='utf8'))
    if not os.path.exists(output_dir + '/buggy_lines'):
        os.mkdir(output_dir + '/buggy_lines')
    if not os.path.exists(output_dir + '/buggy_methods'):
        os.mkdir(output_dir + '/buggy_methods')
    if not os.path.exists(output_dir + '/buggy_classes'):
        os.mkdir(output_dir + '/buggy_classes')
    if not os.path.exists(output_dir + '/metas'):
        os.mkdir(output_dir + '/metas')
    if not os.path.exists(output_dir + '/fix_lines'):
        os.mkdir(output_dir + '/fix_lines')
    if not os.path.exists(output_dir + '/fix_methods'):
        os.mkdir(output_dir + '/fix_methods')
    if not os.path.exists(output_dir + '/fix_classes'):
        os.mkdir(output_dir + '/fix_classes')
    ind=1
    success_ids=[]
    for info in all_infos:
        id=info["_id"]["$oid"]
        if id in ids:
            try:
                print(ind,id)
                ind+=1
                err=info['errs'][0]
                buggy_line='\n'.join([line.strip() for line in err["src_content"]])
                fix_line='\n'.join([line.strip() for line in err["tgt_content"]])
                buggy_method=info['buggy_code']
                fix_method=info['fix_code']

                parent_id=info['parent_id']
                file_path=parent_id.split('@')[0]
                buggy_class=class_dir+'/'+'/'.join(file_path.split('\\'))
                fix_class=buggy_class.replace('P_dir','F_dir')
                meta = bench + '<sep>' + id + '<sep>' + err['src_pos'] + '<sep>' + err['tgt_pos'] \
                       + '<sep>' + parent_id + '<sep>' + info['type_errs']

                with open(output_dir+'/buggy_lines/'+id+'.txt','w',encoding='utf8')as f:
                    f.write(buggy_line)
                    f.close()

                with open(output_dir+'/fix_lines/'+id+'.txt','w',encoding='utf8')as f:
                    f.write(fix_line)
                    f.close()

                with open(output_dir+'/buggy_methods/'+id+'.txt','w',encoding='utf8')as f:
                    f.write(buggy_method)
                    f.close()

                with open(output_dir + '/fix_methods/' + id + '.txt', 'w', encoding='utf8') as f:
                    f.write(fix_method)
                    f.close()

                with open(output_dir + '/metas/' + id + '.txt', 'w', encoding='utf8') as f:
                    f.write(meta)
                    f.close()

                copyfile(buggy_class,output_dir+'/buggy_classes/'+id+'.java')
                copyfile(fix_class,output_dir+'/fix_classes/'+id+'.java')
                success_ids.append(id)
            except:
                continue



    with open(output_dir+'/trn.ids','w',encoding='utf8')as f:
        for id in success_ids:
            f.write(id+'\n')

def extract_ids_4train(exclude_repos_f,commit_repos_f,all_ids_json,output_f):
    exclude_repos=readF2L(exclude_repos_f)
    commits_repos=json.load(codecs.open(commit_repos_f,'r',encoding='utf8'))
    all_ids_json=json.load(codecs.open(all_ids_json,'r',encoding='utf8'))
    trn_ids={}
    ind=0
    rej=0
    for id in all_ids_json.keys():
        commit=all_ids_json[id]["commit"]
        try:
            repo=commits_repos[commit]
        except:
            continue
        skipflag=0
        for ex_repo in exclude_repos:
            if ex_repo in repo:
                skipflag=1
                rej+=1
                break
        if skipflag==0:
            ind+=1
            print("accept ",str(ind)," reject ",str(rej))
            trn_ids[id]=all_ids_json[id]
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(trn_ids,f,indent=2)

def extract_val_ids(val_dir,commit_repo_f,bug_info_f,output_f):
    oneline_ids=json.load(codecs.open(bug_info_f,'r',encoding='utf8'))
    commit_repo=json.load(codecs.open(commit_repo_f,'r',encoding='utf8'))
    files=os.listdir(val_dir)
    special_repos=[]

    val_ids=[]
    for file in files:
        minfo=codecs.open(val_dir+'/'+file,'r',encoding='utf8').read().strip()
        special_commit=minfo.split('<sep>')[4].split('\\')[0]
        special_repos.append(commit_repo[special_commit])
    for id in oneline_ids.keys():
        commit=oneline_ids[id]
        if commit in commit_repo.keys():
            repo=commit_repo[commit]
        else:
            continue
        if repo in special_repos:
            val_ids.append(id)
    with open(output_f,'w',encoding='utf8')as f:
        for id in val_ids:
            f.write(id+'\n')
        f.close()


    pass

def filter_ids_4train(ids_json,output_f):
    def get_mod_lines(pos):
        newpos=pos.replace('[','').replace(']','')
        infos=newpos.split(':')
        return int(infos[1])-int(infos[0])
    ids_info=json.load(codecs.open(ids_json,'r',encoding='utf8'))
    all_ids=[]
    ind=0
    for id in ids_info:
        src_pos=ids_info[id]["src_pos"]
        tgt_pos=ids_info[id]["tgt_pos"]
        src_mod_lines=get_mod_lines(src_pos)
        tgt_mod_lines=get_mod_lines(tgt_pos)
        if (src_mod_lines+tgt_mod_lines)<4:
            all_ids.append(id)
            ind+=1
            print(ind)
    with open(output_f,'w',encoding='utf8')as f:
        for line in all_ids:
            f.write(line+'\n')


    pass

def extract_allids_oneline(buggy_info_f,output_f):
    buggy_infos=json.load(codecs.open(buggy_info_f,'r',encoding='utf8'))
    id_commits={}
    ind=0
    for binfo in buggy_infos:
        id=binfo["_id"]["$oid"]
        commit_sha=binfo["parent_id"].split('\\')[0]
        num_errs=binfo["num_errs"]
        print("num_errs",num_errs)
        if num_errs==1:
            err=binfo["errs"][0]
            id_commits[id]={"commit":commit_sha,"src_pos":err["src_pos"],"tgt_pos":err["tgt_pos"]}

            ind+=1
            print(ind)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(id_commits,f,indent=2)
extract_insertion_dataset("E:/NPR4J/QuixBugs-master/QuixBugs-master/java_programs","E:/NPR4J/QuixBugs-master/QuixBugs-master/correct_java_programs","qbs",r"E:\NPR4J\MongoDB_output\Binfo_quixbugs.json","E:/NPR4J/InsertionData")
extract_insertion_dataset("D:/huawei项目/Defects4j/BF_Rename",
                          "D:/huawei项目/Defects4j/BF_Rename",
                          "d4j",r"E:\NPR4J\MongoDB_output\Binfo_d4j.json",
                          "E:/NPR4J/InsertionData")
extract_insertion_dataset("E:/NPR4J/bears_data",
                          "E:/NPR4J/bears_data",
                          "bears",r"E:\NPR4J\MongoDB_output\Binfo_bears.json",
                          "E:/NPR4J/InsertionData")
#extract_allids_oneline(r"/home/zhongwenkang3/NPR4J_Data/Buginfo.json",r"/home/zhongwenkang3/NPR4J_Data/alloneline_ids.json")
#extract_ids_4train("/home/zhongwenkang3/NPR4J_Data/exclude_repos.txt","/home/zhongwenkang3/NPR4J_Data/commit_simple.json","/home/zhongwenkang3/NPR4J_Data/alloneline_ids.json","/home/zhongwenkang3/NPR4J_Data/ids4trn.json")
#filter_ids_4train("/home/zhongwenkang3/NPR4J_Data/ids4trn.json","/home/zhongwenkang3/NPR4J_Data/ids4trn_lt4.json")
#extract_bigdata_4train("/home/zhongwenkang3/bugfixes/sciclone/data10/mtufano/deepLearningMutants/out/bugfixes/code",
#                       "train","/home/zhongwenkang3/NPR4J_Data/ids4trn_lt4.json","/home/zhongwenkang3/NPR4J_Data/Buginfo.json",
#                       "/home/zhongwenkang3/NPR4J_Data/BigTrain")
extract_val_ids("E:/NPR4J/val_meta/RawData/metas", r"E:/NPR4J/commit_simple.json",
                r"E:/NPR4J/alloneline_ids.json", r"E:/NPR4J/all_valids.txt")