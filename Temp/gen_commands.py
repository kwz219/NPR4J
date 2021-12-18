import os
Defects4j_pros=["Chart","Cli","Closure","Codec","Collections","Compress","Csv","Gson","JacksonCore","JacksonDatabind","JacksonXml","Jsoup"
              ,"JxPath","Lang","Math","Mockito","Time"]
def gen_commands():
    projects=["Chart","Cli","Closure","Codec","Collections","Compress","Csv","Gson","JacksonCore","JacksonDatabind","JacksonXml","Jsoup"
              ,"JxPath","Lang","Math","Mockito","Time"]
    for pro in projects:
        command="framework/bin/defects4j query  -p "+ str(pro)+" -q 'project.id,project.name,revision.id.fixed,classes.modified' -o infos/"+str(pro)+".csv"
        print(command)
        #os.system(command)
#gen_commands()
l=[1,2,3,4]
for i,item in enumerate(l):
    print(i,item)
print(l.index(3))
print(l[:3])