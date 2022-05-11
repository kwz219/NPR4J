
#!/usr/bin/python
import json
import sys, os, subprocess,fnmatch, shutil, csv,re, datetime
import time                       
import codecs
import argparse
import javalang
def getResults(bugindex,change_dict,root,projects_dir):
        #Step 1, get bug inforation from bugId
        #bugId,buggyFile,lineNo,action = getInfoFromIndex(bugindex,root)
        #print(bugId,buggyFile,lineNo,action)
        print('========'+root+'======')
        #compile script location
        scriptdir = root+'/bears-benchmark/scripts'
        os.chdir(scriptdir)
        print('now in the dir:'+scriptdir )
        repodir = root+'/'+projects_dir
        checkoutstring = 'python2 checkout_bug.py  --bugId  '+ bugindex + '  --workspace '+ repodir
        #customized script to allow test running
        compilestring = 'python2 compile_bug.py  --bugId  '+ bugindex + '  --workspace '+ repodir
        print(checkoutstring)
        #os.system(checkoutstring)
        projectdir = repodir + '/' + bugindex
        os.chdir(projectdir)
        os.system("mvn clean")
        #apply patch
        os.chdir(repodir)   

        #prepare the diff
        for file in change_dict.keys():

            projectPath = repodir+'/' + bugindex + '/' + file
            print('projectPath:', projectPath)
            #print(change_dict.get(file))
            if True:

                filename=file.split('/')[-1]
                originFile = repodir+'/' + bugindex + '_'+filename.replace(".java","_tmp.java")

                os.system('mv ' + projectPath + ' ' + originFile)

                with open(projectPath, 'w',encoding='utf8') as targetfile:
                    targetfile.write(change_dict[file])
                    targetfile.close()
        #prepare_diff(bugId,buggyFile,preds,lineNo,action,root)
    
        os.chdir(scriptdir)
        print(compilestring)
        results = os.popen(compilestring).read()
        compile_error = True
        PassHumanTest = False
        execResult=""
        print(results)
        for line in results.split('\n'):
            if 'BUILD SUCCESS' in line:
                print(line)
                compile_error = False
                break
        print("compile_error",compile_error)
        if not compile_error:
            execResult = 'successcompile'
            teststring='python2 run_tests_bug.py --bugId '+bugindex+' --workspace '+repodir
            testresults = os.popen(teststring).read()
            print(testresults)
            useful_info=testresults.split("Results :")[-1]
            for line in useful_info.split('\n'):
                if 'Failures: 0' in line and 'Errors: 0' in line:
                    execResult = 'passHumanTest'
                    print('Plausible!!')
                    break
        else:
            execResult= "failcompile"
        #Recovery
        for file in change_dict.keys():
            originFile = repodir + '/'+bugindex + '_'+filename.replace(".java","_tmp.java")
            rm_str='rm -rf '+repodir + '/' +bugindex+'/'+ file
            recovery_str='mv  ' + originFile + '  ' + repodir + '/' +bugindex+'/'+ file
            os.system(rm_str)
            os.system(recovery_str)
        #print(recovery_str)

        print("execResult",execResult)
        return execResult

        

def prepare_diff(bugId,buggyFile,preds,lineNo,action,root):
    print('buggyFile:',buggyFile)
    
    project = root+'/bears-projects/'
    projectPath = project+bugId+'/'+buggyFile
    print('projectPath:',projectPath)
    
    if not os.path.exists(projectPath):
        return 'NoExist'
    else:
        originFile = project+bugId+'_tmp.java'

        os.system('mv '+projectPath+' '+originFile)

        with open(projectPath,'w') as targetfile:
            targetfile.write(preds)

        
        
        
        
        
def getInfoFromIndex(bugIndex,root):
    print("BearsDiscriminator getInfoFromIndex: ",bugIndex)
    bugname= ''
    buggyFile=''
    lineNo=''
    action=''
    with open (root+'/BearsMeta.csv','r') as metafile:
        lines = metafile.readlines()
        for line in lines:
            if str(bugIndex) in line.split('\t')[1] and line.split('\t')[1] in str(bugIndex):
                bugname = line.split('\t')[1]
                buggyFile = line.split('\t')[2]
                lineNo = line.split('\t')[3]
                action = line.split('\t')[4]
                break
    
    return bugname,buggyFile,lineNo,action




def get_valid_modify(changedict:dict):
    change_file={}
    for id in changedict.keys():
        if changedict[id]['file_path'].endswith("Test.java"):
            continue
        else:
            change_file[changedict[id]['file_path']]='init'
    return change_file
def get_min_ids(changedict:dict,patches_f):
    candi_count=200
    for id in changedict.keys():
        if changedict[id]['file_path'].endswith("Test.java"):
            continue
        else:
            if id not in patches_f.keys():
                return -1
            patches_count=len(patches_f[id]["patches"].keys())
            candi_count=min(candi_count,patches_count)
    return candi_count
def get_fixed_code(raw_method, new_method, java):
    def get_tokenized_str(code):
        tokens = list(javalang.tokenizer.tokenize(code))
        tokens = [t.value for t in tokens]
        return ' '.join(tokens)
    raw_str = get_tokenized_str(raw_method)
    new_str = get_tokenized_str(new_method)
    java_str = get_tokenized_str(java)
    if raw_str in java_str:
        print("Replace Finished.")
    return java_str.replace(raw_str, new_str)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run_Bears.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-bears_f",required=True)
    parser.add_argument("-patches_f", help="",required=True)
    parser.add_argument("-sys",required=True)
    parser.add_argument("-project_path", required=True)
    opt = parser.parse_args()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    #getResults('10','if  (channel  !=  null  &&  channel.getPipeline().get(HttpRequestDecoder.class)  !=  null')
    bears_f=codecs.open(opt.bears_f,'r',encoding='utf8')
    patches_f=codecs.open(opt.patches_f,'r',encoding='utf8')

    bears_bugs=json.load(bears_f)
    patches_info=json.load(patches_f)
    bugids=["Bears-"+str(i) for i in range(1,252)]
    """
    content=patches_info["bears_6257cdb15fef470c3d70c259"]["patches"]["0"]
    content=bears_bugs["Bears-112"]["bears_6257cdb15fef470c3d70c259"]["classcontent"]
    change_dict={"src/org/traccar/protocol/L100ProtocolDecoder.java":content}
    result1=getResults("Bears-112",change_dict,"/root/zwk/Eval_bears","")
    print("EvalResult: ",result1)
    """
    for bugId in bugids:
        #deal with Bears-N
        skipflag=0
        checklist=["Bears-195","Bears-202","Bears-158","Bears-208","Bears-10","Bears-12","Bears-27","Bears-38","Bears-29","Bears-31","Bears-33","Bears-28","Bears-44","Bears-45"
                   "Bears-35","Bears-39","Bears-37","Bears-40","Bears-42","Bears-43","Bears-48","Bears-55","Bears-56","Bears-58","Bears-67","Bears-68","Bears-69","Bears-77","Bears-78",
                   "Bears-82","Bears-84","Bears-87","Bears-90","Bears-91","Bears-94","Bears-191","Bears-49","Bears-53","Bears-60","Bears-59","Bears-64"]

        if bugId in checklist or  (not bugId in bears_bugs.keys()) :
            continue
        change_dict = bears_bugs[bugId]
        change_file=get_valid_modify(change_dict)
        if len(change_file)==0:
            continue
        else:
            id_range=get_min_ids(change_dict,patches_info)
            if id_range==-1:
                skipflag=1
            for i in range(id_range):
                change_file = get_valid_modify(change_dict)
                if skipflag == 1:
                    continue
                for id in change_dict.keys():
                    if id not in patches_info.keys():
                        continue
                    per_id_dict=change_dict[id]
                    file_path=per_id_dict["file_path"]
                    if file_path in change_file.keys():
                        if change_file[file_path]=='init':
                            classcontent=per_id_dict["classcontent"]
                        else:
                            classcontent=change_file.get(file_path)
                        buggymethod=per_id_dict['buggy_method']

                        patch_candidata=patches_info[id]['patches'][str(i)]
                        #print(i,patch_candidata)
                        try:
                            new_class=get_fixed_code(buggymethod,patch_candidata,classcontent)
                        except:
                            new_class=classcontent

                        change_file.update({file_path:new_class})


                print(bugId,change_file.keys())
                result=getResults(bugId,change_file,"/home/zhongwenkang/Eval_bears",opt.project_path)

                with open("/home/zhongwenkang/Eval_bears/"+opt.sys+"_eval.result",'a',encoding='utf8')as f:
                    f.write(bugId+" "+str(i)+" "+result+'\n')
                    f.close()
                if result=="passHumanTest":
                    skipflag=1
                    with open("/home/zhongwenkang/Eval_bears/"+opt.sys+'_'+bugId+"_right."+str(i),'w',encoding='utf8')as wf:
                        json.dump(change_file,wf,indent=2)
                        wf.close()





