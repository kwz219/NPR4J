
import csv
import os
Defects4j_pros=["Chart","Cli","Closure","Codec","Collections","Compress","Csv","Gson","JacksonCore","JacksonDatabind","JacksonXml","Jsoup"
              ,"JxPath","Lang","Math","Mockito","Time"]
"""
Extract bug-fix files from Defects4j
"""
def locate_files(buginfo_dir,projects_dir):
    for pro in Defects4j_pros:
        #os.system("mkdir "+pro)
        #using defects4j query command to get these csv files
        csv_path=buginfo_dir+"/"+pro+".csv"
        bug_infos=[]
        with open(csv_path,'r',encoding='utf8')as cf:
            reader=csv.reader(cf)
            for row in reader:
                major_info=row[:-1]
                major_info.append([cls.replace(".","/")+".java" for cls in row[-1].split(";")])
                bug_infos.append(major_info)
            cf.close()

        for bug_info in  bug_infos:
            bugid=bug_info[0]
            proname=bug_info[1]
            pro_ori=bug_info[2]
            revision_id=bug_info[3]
            mod_files=bug_info[4]
            for file in mod_files:
                filename=file.split("/")[-1]
                buggy_path=projects_dir+"/"+proname+"_"+bugid+"_buggy"+"/src/"+file
                fix_path = projects_dir + "/" + proname + "_" + bugid + "_fix" + "/src/" + file
                if proname=="Chart":
                    buggy_path=buggy_path.replace("src","CoCoNut")
                    fix_path=fix_path.replace("src","CoCoNut")
                elif proname in ["Codec","JxPath"] or (proname=="Cli" and int(bugid)<=30) or(proname=="Math" and int(bugid)>84)or(proname=="Lang" and int(bugid)>35) or (proname=="Codec" and int(bugid)<11):
                    buggy_path = buggy_path.replace("src/", "src/java/")
                    fix_path = fix_path.replace("src/", "src/java/")
                elif proname in ["Time","Jsoup","JacksonCore","JacksonDatabind","Compress","Csv","JacksonXml"]or (proname=="Codec" and int(bugid)>=11) or (proname=="Cli" and int(bugid)>30)or(proname=="Lang" and int(bugid)<=35) or (proname=="Math" and int(bugid)<=84):
                    buggy_path = buggy_path.replace("src/", "src/main/java/")
                    fix_path = fix_path.replace("src/", "src/main/java/")
                elif proname =="Gson":
                    buggy_path = buggy_path.replace("src/", "gson/src/main/java/")
                    fix_path = fix_path.replace("src/", "gson/src/main/java/")
                command1="cp "+buggy_path+"   "+proname+"_"+bugid+"_buggy_"+filename
                command2="cp "+fix_path+"   "+proname+"_"+bugid+"_fix_"+filename
                #print(command1,command2)
                os.system("cp "+buggy_path+"   "+proname+"_"+bugid+"_buggy_"+filename)
                os.system("cp "+fix_path+"   "+proname+"_"+bugid+"_fix_"+filename)



locate_files("../infos","../code")



