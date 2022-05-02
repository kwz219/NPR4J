import javalang
import codecs
import json

from bson import ObjectId
import os

from Utils.IOHelper import readF2L
import pymongo
MONGO_URL="mongodb://localhost:27017/"
DATABASE="BF_Methods"
class MongoHelper(object):
    def __init__(self):
        self.mongoClient=pymongo.MongoClient(MONGO_URL)
        self.db=self.mongoClient[DATABASE]
    def get_col(self,COL_NAME):
        return self.db[COL_NAME]

def generate_classcontent(path,output_path,id):
    codecontent=codecs.open(path,'r',encoding='utf8').read().strip()
    #print(codecontent)
    tree = javalang.parse.parse(codecontent)
    package_name=tree.package.name
    #print(package_name)
    #print(tree)
    i=1
    filename=path.split('\\')[-1]
    classcontent={"filename":filename,"package_name":package_name,"classes":[]}
    for clspath,clsnode in tree.filter(javalang.tree.ClassDeclaration):
        classname=getattr(clsnode,"name")
        #print("classname: ",classname)
        class_dict = {"methods": [], "fields": [], "name":classname}
        for path,node in clsnode.filter(javalang.tree.MethodDeclaration):
            node_name = getattr(node, "name")
            return_type = getattr(node, "return_type")
            if return_type == None:
                return_type_name = None
            else:
                return_type_name = getattr(return_type, "name")
            parameters = getattr(node, "parameters")
            if len(parameters) == 0:
                simp_parameters = []
            else:
                simp_parameters = []
                for pa in parameters:
                    pa_name = getattr(pa, "name")
                    pa_type = getattr(getattr(pa, "type"), "name")
                    pa_item = {"name": pa_name, "type": pa_type}
                    simp_parameters.append(pa_item)
            method_dict = {"params": simp_parameters, "name": node_name,"type":return_type_name}
            #print("$", "methods", "$ -------------------------")
            #print(node_name)
            #print(simp_parameters)
            #print(return_type_name)
            i = i + 1

            new_methods=class_dict.get("methods")
            new_methods.append(method_dict)
            #print("new_methods",new_methods)
            class_dict["methods"]=new_methods
            #print(class_dict["methods"])

        for path,node in clsnode.filter(javalang.tree.FieldDeclaration):
            field_dec=getattr(node,"declarators")
            field_type=getattr(node,"type")

            field_name=getattr(field_dec[0],"name")
            field_type_name=getattr(field_type,"name")

            #print("$", "Field", "$ -------------------------")
            #print(field_name)
            #print(field_type_name)
            i+=1
            field_dict={"name":field_name,"type":field_type_name}
            new_fields=class_dict.get("fields")
            new_fields.append(field_dict)
            class_dict["fields"]=new_fields
        new_classes=classcontent.get("classes")

        new_classes.append(class_dict)
        classcontent["classes"]=new_classes
    with open(output_path+"/"+id+".classcontent","w",encoding='utf8')as f:
        json.dump([classcontent],f,indent=2)

def generate_4benchmark(dir,output_dir):
    mongoClient = MongoHelper()
    d4jids=readF2L(dir+'/d4j.ids')
    bearsids=readF2L(dir+'/bears.ids')
    bdjarids=readF2L(dir+'/bdjar.ids')
    qbsids=readF2L(dir+'/qbs.ids')
    d4j_col=mongoClient.get_col("Binfo_d4j")
    bears_col = mongoClient.get_col("Binfo_bears")
    bdjar_col = mongoClient.get_col("Binfo_bdjar")
    qbs_col = mongoClient.get_col("Binfo_quixbugs")
    failed_ids=[]
    i=1
    correct_i=0
    error_i=0
    for id in d4jids:
        try:
            bug = d4j_col.find_one({'_id': ObjectId(id)})
            parentid=bug['parent_id']
            file_path=parentid.split("@")[0]
            generate_classcontent(file_path,output_dir,id)
            correct_i+=1
        except:
            failed_ids.append(id)
            error_i+=1
        i=i+1
        print("correct: ",correct_i," error: ",error_i)
    for id in bearsids:
        try:
            bug = bears_col.find_one({'_id': ObjectId(id)})
            parentid=bug['parent_id']
            file_path=parentid.split("@")[0]
            generate_classcontent(file_path,output_dir,id)
            correct_i += 1
        except:
            failed_ids.append(id)
            error_i += 1
        i = i + 1
        print("correct: ", correct_i, " error: ", error_i)
    for id in bdjarids:
        try:
            bug = bdjar_col.find_one({'_id': ObjectId(id)})
            parentid=bug['parent_id']
            file_path=parentid.split("@")[0]
            generate_classcontent(file_path,output_dir,id)
            correct_i += 1
        except:
            failed_ids.append(id)
            error_i += 1
        i = i + 1
        print("correct: ", correct_i, " error: ", error_i)
    for id in qbsids:
        try:
            bug = qbs_col.find_one({'_id': ObjectId(id)})
            parentid=bug['parent_id']
            file_path=parentid.split("@")[0]
            generate_classcontent(file_path,output_dir,id)
            correct_i += 1
        except:
            failed_ids.append(id)
            error_i += 1
        i = i + 1
        print("correct: ", correct_i, " error: ", error_i)

def generate_4diverse(ids_f,output_dir,filedir):
    ids=readF2L(ids_f)
    mongoClient = MongoHelper()
    bug_col = mongoClient.get_col("Buginfo")
    failed_ids=[]
    i=1
    correct_i=0
    error_i=0
    father_dict={}
    for id in ids[15000:]:
        metas=codecs.open("F:/NPR_DATA0306/Evaluationdata/Diversity/metas/"+id+'.txt','r',encoding='utf8').read().strip().split('<sep>')
        id=metas[1]
        father_file=metas[4].split('@')[0]

        if father_file not in father_dict.keys():
            new_ids=[id]
            father_dict[father_file]=new_ids
        else:
            ids=father_dict.get(father_file)
            ids.append(id)
            father_dict[father_file] = ids
        try:
            bug = bug_col.find_one({'_id': ObjectId(id)})
            parentid=bug['parent_id']
            file_path=parentid.split("@")[0]

            #print(father_dict)
            for sameid in father_dict.get(father_file):
                #print(output_dir+"/"+sameid+".classcontent")
                if os.path.exists(output_dir+"/"+sameid+".classcontent"):
                    print("exists")
                    correct_i += 1
                    continue
            else:
                print("don't")
            generate_classcontent(filedir+file_path,output_dir,id)
            #correct_i += 1
        except:
            failed_ids.append(id)
            error_i += 1
        i = i + 1
        print("correct: ", correct_i, " error: ", error_i)
    with open(output_dir+"/father_dict_15k_after.json",'w',encoding='utf8')as f:
        json.dump(father_dict,f,indent=2)
#generate_4benchmark("F:/NPR_DATA0306/Evaluationdata/Benchmark","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/Recoder")
generate_4diverse("F:/NPR_DATA0306/Evaluationdata/Diversity/success.ids","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder","E:/bug-fix/")