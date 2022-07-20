import argparse
import codecs
import json
import os
import subprocess
import sys
import javalang
from tqdm import tqdm
def getResults(bugIndex, preds,meta_f,rootPath,log_file):
    print("QuixBugsDiscriminator getResults")
    #print("preds" + preds)

    bugId, buggyFile, lineNo = getInfoFromIndex(bugIndex,meta_f)
    lineNo = lineNo.replace('\n', '').replace('\t', '')
    print("bugId, buggyFile, lineNo: " + bugId, buggyFile, lineNo)
    with open(log_file, 'a', encoding='utf8') as log_f:
        log_f.write('bugId, buggyFile, lineNo: '+' '.join([bugId, buggyFile, lineNo]) + '\n')
        log_f.close()
    # The bug path:
    quixbugroot = rootPath+'/quixbugs-experiment'
    current_bug = quixbugroot + buggyFile
    print("current_bug: " + current_bug)
    with open(log_file, 'a', encoding='utf8') as log_f:
        log_f.write('current_bug: '+current_bug + '\n')
        log_f.close()
    # Get predicts and generate diffs:
    project_path = rootPath+'/quixbugs-experiment/tmp/' + bugId

    prepare_diff(project_path, bugId, current_bug, preds)

    # copy and replace the patch file to buggyFile
    os.system('cp  ' + project_path + '/' + bugId + '.java  ' + current_bug)

    # compile
    os.chdir(quixbugroot)
    result = os.popen('mvn compile').read()
    with open(log_file, 'a', encoding='utf8') as log_f:
        log_f.write("Compiling Result &&&&&&&&&" +'\n')
        log_f.write(result + '\n')
        log_f.write("Compiling End &&&&&&&&&" + '\n')
        log_f.close()
    #print(result)
    os.chdir('..')

    lines = result.split('\n')

    compile_error = True
    PassHumanTest = False
    for line in lines:
        if 'BUILD SUCCESS' in line:
            compile_error = False

    if compile_error:
        # The end back to the original buggy file
        os.system('mv  ' + project_path + '/' + bugId + '.java    ' + project_path + '/' + bugId + '_target.java')
        os.system('mv  ' + project_path + '/' + bugId + '_origin.java  ' + project_path + '/' + bugId + '.java')
        os.system('cp  ' + project_path + '/' + bugId + '.java  ' + current_bug)
        os.system('rm -rf  ' + project_path)

        return "failcompile"

    else:
        # BUILD SUCCESS and check human test
        # cp test:

        testname = bugId
        rootpath = quixbugroot

        cptstring = 'cp ' + rootpath + '/src/test/java/java_programs/' + testname + '_TEST.java   ' + rootpath + '/target/classes/java_programs'
        # compile tests
        cpilestr = 'javac -cp ' + rootpath + '/target/classes:' + rootpath + '/libs/junit-4.12.jar:' + rootpath + '/libs/hamcrest-core-1.3.jar:' + rootpath + '/target/classes  ' + rootpath + '/target/classes/java_programs/' + testname + '_TEST.java'

        print(cptstring)
        os.system(cptstring)

        print(cpilestr)
        os.system(cpilestr)

        exestr = 'timeout 40 java -cp ' + rootpath + '/target/classes:' + rootpath + '/libs/hamcrest-core-1.3.jar:' + rootpath + '/libs/junit-4.12.jar org.junit.runner.JUnitCore  java_programs.' + testname + '_TEST'
        print(exestr)

        result = os.popen(exestr).read()
        with open(log_file, 'a', encoding='utf8') as log_f:
            log_f.write("Testing Result &&&&&&&&&" + '\n')
            log_f.write(result + '\n')
            log_f.write("Testing End &&&&&&&&&" + '\n')
            log_f.close()
        print('This is the human test result')
        print(result)

        if 'OK' in result:
            PassHumanTest = True

        os.system('mv  ' + project_path + '/' + bugId + '.java    ' + project_path + '/' + bugId + '_target.java')
        os.system('mv  ' + project_path + '/' + bugId + '_origin.java  ' + project_path + '/' + bugId + '.java')
        os.system('cp  ' + project_path + '/' + bugId + '.java  ' + current_bug)
        os.system('rm -rf  ' + project_path)

        if not PassHumanTest:

            return "successcompile"
        else:
            return "passHumanTest"

        #         else:


#             #  to check if pass Evosuite tests
#             cptstring = 'cp '+rootpath+'/generatedTests/seed_1/evosuite-tests/java_programs/'+testname+'_ESTest.java   '+ rootpath+'/target/classes/java_programs'
#             #compile tests
#             cpilestr='javac -cp '+rootpath+'/libs/evosuite-standalone-runtime-1.0.6-SNAPSHOT.jar:'+rootpath+'/libs/junit-4.12.jar:'+rootpath+'/libs/hamcrest-core-1.3.jar:'+rootpath+'/target/classes   '+rootpath+'/target/classes/java_programs/'+testname+'_ESTest.java'
#             #execute tests
#             exestr='timeout 60 java -cp '+rootpath+'/target/classes:'+rootpath+'/libs/evosuite-standalone-runtime-1.0.6-SNAPSHOT.jar:'+rootpath+'/libs/hamcrest-core-1.3.jar:'+rootpath+'/libs/junit-4.12.jar org.junit.runner.JUnitCore  java_programs.'+testname+'_ESTest'


#             os.system(cptstring)
#             os.system(cpilestr)
#             result=os.popen(exestr).read()
#             print('This is the RGT test result')
#             print(result)

#             if 'OK' in result:
#                 PassRGTTest =  True

#             os.system('mv  '+project_path+'/'+bugId+'.java    '+project_path+'/'+bugId+'_target.java')
#             os.system('mv  '+project_path+'/'+bugId+'_origin.java  '+ project_path+'/'+bugId+'.java' )
#             os.system('cp  ' +project_path+'/'+bugId+'.java  '+current_bug)
#             os.system('rm -rf  ' +project_path)

#             if PassRGTTest:
#                 return "passAllTest"
#             else:
#                 return "passHumanTest"


def prepare_diff(project_path, bugId, bugpath, preds):
    if not os.path.exists(project_path):
        os.system('mkdir -p  ' + project_path)

    os.system('cp  ' + bugpath + ' ' + project_path)

    origin = project_path + '/' + bugId + '_origin.java'
    os.system('mv  ' + project_path + '/' + bugId + '.java' + '  ' + origin)


    print('bugId', bugId)
    print(preds)

    with open(project_path + '/' + bugId + '.java', 'a') as targetfile:
        targetfile.write(preds)


def getInfoFromIndex(bugIndex,meta_f):
    print("QuixBugsDiscriminator getInfoFromIndex")
    #     bugIndex = bugIndex.item()
    print("bugIndex " + str(bugIndex))

    with open(meta_f, 'r') as metafile:
        lines = metafile.readlines()
        for line in lines:
            if str(bugIndex) in line.split(',')[1] and line.split(',')[1] in str(bugIndex):
                return line.split(',')[1], line.split(',')[2], line.split(',')[3]

if __name__ =="__main__":
    parser = argparse.ArgumentParser(
        description='Run_QuixBugs.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-sys", help="", required=True)
    parser.add_argument("-patches_f", help="", required=True)
    parser.add_argument("-benchmarks_f", help="", required=True)
    parser.add_argument("-output_dir",required=True)
    parser.add_argument("-metainfo_f", required=True)
    parser.add_argument("-root_path",required=True)
    opt = parser.parse_args()
    meta_csv_f=opt.metainfo_f
    rootPath=opt.root_path
    sys = opt.sys
    patches_f = opt.patches_f
    benchmarks_f = opt.benchmarks_f
    output_dir = opt.output_dir
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pf = codecs.open(patches_f, 'r', encoding='utf8')
    bf = codecs.open(benchmarks_f, 'r', encoding='utf8')
    pred_patches = json.load(pf)
    benchmarks = json.load(bf)
    results=[]
    log_file=output_dir+'/evaluate.log'
    print("before running, mv QuixFixOracleHelper.java to src/main/java/java_programs !")
    print("before running, mv QuixFixOracleHelper.java to src/main/java/java_programs !")
    print("before running, mv QuixFixOracleHelper.java to src/main/java/java_programs !")
    for id in pred_patches.keys():

        if id in benchmarks.keys() :
            per_patches = pred_patches.get(id)
            id_info = benchmarks.get(id)

            name = id_info["name"]
            if "patches" in per_patches.keys():
                candidates = per_patches["patches"]
            else:
                candidates = per_patches
            skip_flag=0
            for key in candidates.keys():
                if not skip_flag==1:
                    patch = candidates.get(key)

                    if "Tufano" in opt.sys:
                        if "METHOD_" in  patch or "VAR_" in patch or "STRING_" in patch or "INT_" in patch:
                            with open(os.path.join(output_dir, sys + '_eval.result'), 'a', encoding='utf8') as f:
                                f.write(' '.join([id, name, key, "failconcretize"]) + '\n')
                                f.close()
                            continue
                    print("keys:$$$$$$$$$",key)
                    with open(log_file,'a',encoding='utf8')as log_f:
                        log_f.write("keys:$$$$$$$$$ "+key+'\n')
                        log_f.close()
                    try:
                        tok_patch = patch
                        buggy_method=id_info["buggy_method"]
                        ori_class=id_info["classcontent"]
                        if buggy_method in ori_class:
                            new_class = ori_class.replace(buggy_method,tok_patch)
                            eval_result=getResults(name,new_class,meta_csv_f,rootPath,log_file)
                            print(id,name,key,eval_result)
                            with open(log_file, 'a', encoding='utf8') as log_f:
                                log_f.write(' '.join([id,name,key,eval_result]) + '\n')
                                log_f.close()
                            with open(os.path.join(output_dir,sys+'_eval.result'),'a',encoding='utf8')as f:
                                f.write(' '.join([id,name,key,eval_result])+'\n')
                                f.close()
                            if eval_result=="passHumanTest":
                                with open(os.path.join(output_dir,sys+"_"+name+"_passTest_"+key+".patch"),'w',encoding='utf8')as f:
                                    f.write(patch)
                                    f.close()
                    except:
                        with open(os.path.join(output_dir,sys+'_eval.result'),'a',encoding='utf8')as f:
                            f.write(' '.join([id,name,key,'failtokenize'])+'\n')
                            f.close()


