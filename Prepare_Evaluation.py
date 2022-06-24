import codecs
import json


def Prepare_Tufano_patches(recovery_preds_f,output_f,input_dir,benchmark,benchmark_bugs):
    if benchmark=="bears":
        bug_infos=json.load(codecs.open(benchmark_bugs))
        for bugID in bug_infos.keys():
            if len(bug_infos.keys())==1:
                bears_id=list(bug_infos.keys())[0]
                buggy_line=codecs.open(input_dir+'/buggy_lines/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                fix_line=codecs.open(input_dir+'/fix_lines/'+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                buggy_method=bug_infos[bears_id]["buggy_method"].replace('\t',' ').split('\n')
                fix_method=bug_infos[bears_id]["fix_method"].replace('\t',' ').split('\n')
                check_dict={"BugID":bugID,"buggy_method":buggy_method,"fix_method":fix_method,"buggy_line":buggy_line,"fix_line":fix_line}

                plausible_dict={}
                for eval_name in all_dict.keys():
                    bug_eval_re=all_dict.get(eval_name)
                    bug_patches=candidates_dict[eval_name]
                    if bugID in bug_eval_re.keys():
                        ind=bug_eval_re[bugID]
                        candidate=bug_patches[bears_id]["patches"][str(ind)]
                        plausible_dict[eval_name]={"manual_check":"None","reason":"None","pred":candidate.replace('\t',' ').split('\n')}
                if len(plausible_dict)>0:
                    check_dict["plausible_patches"]=plausible_dict
                    with open(output_dir+'/'+bugID+".check",'w',encoding='utf8')as df:
                        json.dump(check_dict,df,indent=2)
                    print(bugID,"finished")
            else:
                ids=list(bug_infos.keys())
                check_dict = {"BugID": bugID}
                hit_count=0
                for idx,bears_id in enumerate(ids):
                    buggy_line=codecs.open(buggy_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                    fix_line=codecs.open(fix_lines_dir+'/'+bears_id+'.txt','r',encoding='utf8').read().strip()
                    buggy_method = bug_infos[bears_id]["buggy_method"].split('\n')
                    fix_method = bug_infos[bears_id]["fix_method"].split('\n')
                    check_dict["buggy_method"+'_'+str(idx)]=buggy_method
                    check_dict["fix_method"+'_'+str(idx)]=fix_method
                    check_dict["buggy_line" + '_' + str(idx)] = buggy_line
                    check_dict["fix_line" + '_' + str(idx)] = fix_line
                    plausible_dict = {}
                    for eval_name in all_dict.keys():
                        bug_eval_re = all_dict.get(eval_name)
                        bug_patches = candidates_dict[eval_name]
                        if bugID in bug_eval_re.keys():
                            hit_count+=1
                            ind = bug_eval_re[bugID]
                            print(eval_name,bears_id,str(ind))
                            try:
                                candidate = bug_patches[bears_id]["patches"][str(ind)]
                            except:
                                continue
                            if eval_name in plausible_dict.keys():
                                plausible_dict[eval_name+"_"+str(idx)]["pred"] = candidate
                            else:
                                plausible_dict[eval_name+"_"+str(idx)]={"manual_check":"None","reason":"None","pred":candidate.replace('\t',' ').split('\n')}
                    if len(plausible_dict.keys()) > 0:
                        check_dict["plausible_patches_"+str(idx)] = plausible_dict
                if hit_count>1:
                    with open(output_dir+'/'+bugID+".check",'w',encoding='utf8')as df:
                         json.dump(check_dict,df,indent=2)
                         print(bugID,"finished")