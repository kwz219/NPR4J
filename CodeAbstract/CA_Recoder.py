import javalang
import codecs
import json

from bson import ObjectId

from Dataset.MongoHelper import MongoHelper
from Utils.IOHelper import readF2L


def generate_classcontent(path,output_path):
    codecontent=codecs.open(path,'r',encoding='utf8').read().strip()
    #print(codecontent)
    tree = javalang.parse.parse(codecontent)
    package_name=tree.package.name
    #print(package_name)
    #print(tree)
    i=1

    classcontent={"filename":path.split("/")[-1],"package_name":package_name,"classes":[]}
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
    with open(output_path,"w",encoding='utf8')as f:
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

#generate_4benchmark("F:/NPR_DATA0306/Evaluationdata/Benchmark","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/Recoder")