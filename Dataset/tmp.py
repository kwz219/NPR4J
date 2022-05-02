import codecs
import json
import os

import javalang
from bson import ObjectId

from CA_SequenceR import MongoHelper
from Utils.IOHelper import readF2L, writeL2F, readF2L_enc


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
def combine_benchmark(dir,postfix):
    d4jfile=dir+'/d4j_.'+postfix
    bdjarfile=dir+'/bdjar_.'+postfix
    qbsfile=dir+'/qbs_.'+postfix
    bearsfile=dir+'/bears_.'+postfix
    d4jlines=readF2L(d4jfile)
    bdjarlines=readF2L(bdjarfile)
    qbslines=readF2L(qbsfile)
    bearslines=readF2L(bearsfile)
    writeL2F(d4jlines+bdjarlines+bearslines+qbslines,dir+'/benchmark.'+postfix)
def get_ids(bench_dir):
    all_methods=os.listdir(bench_dir+'/buggy_methods')
    ids=[]
    for method in all_methods:
        ids.append(method.replace('.txt',''))
    writeL2F(ids,bench_dir+'/benchmark.ids')
def combine_Tufano(buggy_dir,fix_dir,output_dir):
    src_ids=readF2L(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\bears.ids")

    buggy_methods=[]
    fix_methods=[]
    ids=[]
    for sid in src_ids:
        if True:
            sid="bears_"+sid
            buggy_f=buggy_dir+'/'+sid+'.txt_buggy.txt.abs'
            fix_f = fix_dir + '/' + sid + '.txt_buggy.txt.abs'
            buggy_content=codecs.open(buggy_f,'r',encoding='utf8').read().strip()
            fix_content=codecs.open(fix_f,'r',encoding='utf8').read().strip()
            if len(buggy_content)>1 and len(fix_content)>1:
                buggy_methods.append(buggy_content)
                fix_methods.append(fix_content)
                ids.append(sid)
    output_buggy_f=output_dir+'.buggy'
    output_fix_f=output_dir+'.fix'
    output_ids=output_dir+'.ids'
    writeL2F(buggy_methods,output_buggy_f)
    writeL2F(fix_methods,output_fix_f)
    writeL2F(ids,output_ids)

def count_one_method_fix(dict_paths):
    dicts_all={}
    for dict_p in dict_paths:
        dict_f=codecs.open(dict_p,'r',encoding='utf8')
        sub_dict=json.load(dict_f)
        for key in sub_dict.keys():
            if key not in dicts_all.keys():
                dicts_all[key]=sub_dict.get(key)
            else:
                old_ids=dicts_all.get(key)
                old_ids=old_ids+sub_dict.get(key)
                dicts_all[key]=old_ids
    non_one_methods_count=0
    one_count=[]
    for key in dicts_all.keys():
        ids=dicts_all.get(key)
        if len(ids)>1:
            non_one_methods_count+=1
        else:
            one_count.append(ids[0])
    print(non_one_methods_count,one_count)
    with open("F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/father_dict_all.json",'w',encoding='utf8')as f:
        json.dump(dicts_all,f,indent=2)
    writeL2F(one_count,"F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/final.ids")

def prepare_diversity4edits(ids_f,diverse_dir):
    final_ids=readF2L(ids_f)
    diverse_bugs=readF2L_enc(diverse_dir+"/diversity_.buggy",enc="iso8859-1")
    diverse_fixs=readF2L(diverse_dir+"/diversity_.fix")
    diverse_ids=readF2L(diverse_dir+"/diversity_.sids")
    new_bugs=[]
    new_fixs=[]
    new_ids=[]
    assert len(diverse_ids)==len(diverse_bugs) and len(diverse_bugs)==len(diverse_fixs)
    for bug,fix,id in zip(diverse_bugs,diverse_fixs,diverse_ids):
        if id in final_ids:
            new_bugs.append(bug)
            new_fixs.append(fix)
            new_ids.append(id)
    writeL2F(new_bugs,diverse_dir+"/diversity.buggy")
    writeL2F(new_fixs, diverse_dir + "/diversity.fix")
    writeL2F(new_ids, diverse_dir + "/diversity.ids")

#combine_benchmark("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut",'buggy')
#combine_benchmark("F:/NPR_DATA0306/Evaluationdata/Benchmark",'ids')
#combine_benchmark("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut",'fix')
#get_ids(r"F:\NPR_DATA0306\Evaluationdata\Benchmark")
#count_special()
def testjavalang():
    str="public TCredentials toThrift ( Instance instance ) { return new TCredentials ( principal , token . getClass ( ) . getName ( ) , ByteBuffer . wrap ( AuthenticationTokenSerializer . serialize ( token ) ) , instance . getInstanceID ( ) ) ; }"
    toks=javalang.tokenizer.tokenize(str)
    print(toks)
    for tok in toks:
        print(tok)
def writeQuixbugs_f(ids_f,buggy_methods_dir,fix_methods_dir,target_f):
    ids=readF2L(ids_f)
    qbs_ids=[]
    for id in ids:
        if id.startswith("qbs_"):
            qbs_ids.append(id)
    print(len(qbs_ids))
    mongoClient = MongoHelper()
    qbs_col=mongoClient.get_col("Binfo_quixbugs")
    benchmark_dict={}
    for id in qbs_ids:
        objid=id.replace("qbs_","")
        objid=ObjectId(objid)
        buginfo = qbs_col.find_one({"_id":objid})
        parent_f=buginfo["parent_id"]
        file_path=parent_f.split("@")[0]
        name=file_path.split('\\')[-1].replace(".java",'')
        benchmark_dict[id]={"name":name,"buggy_method":codecs.open(buggy_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip(),
                            "fix_method":codecs.open(fix_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip(),
                            "classcontent":codecs.open(file_path,'r',encoding='utf8').read()}
    with open(target_f,'w',encoding='utf8')as df:
        json.dump(benchmark_dict,df,indent=2)
def writeBdjar_f(ids_f,target_f):
    ids=readF2L(ids_f)
    mongoClient = MongoHelper()
    bdjar_col=mongoClient.get_col("Binfo_bdjar")
    benchmark_dict={}
    for id in ids:
        objid = ObjectId(id)
        buginfo = bdjar_col.find_one({"_id": objid})
        parent_id =buginfo["parent_id"]
        file=parent_id.split("@")[0]
        patterns=file.split("\\")
        bug_key=patterns[4]+'_'+patterns[5]
        bug_file=patterns[-1]
        if bug_key not in benchmark_dict.keys():
            benchmark_dict[bug_key]={id:bug_file}
        else:
            old_dict=benchmark_dict.get(bug_key)
            old_dict[id]=bug_file
            benchmark_dict[bug_key]=old_dict
    with open(target_f,'w',encoding='utf8')as df:
        json.dump(benchmark_dict,df,indent=2)

#writeBdjar_f(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\bdjar.ids",r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bdjar.json")

def writeBeras_f(ids_f,buggy_methods_dir,fix_methods_dir,target_f):
    ids=readF2L(ids_f)
    bears_ids=[]
    for id in ids:
        if id.startswith("bears_"):
            bears_ids.append(id)
    print(len(bears_ids))
    mongoClient = MongoHelper()
    bears_col=mongoClient.get_col("Binfo_Bears")
    benchmark_dict={}
    for id in bears_ids:
        objid=id.replace("bears_","")
        objid=ObjectId(objid)
        buginfo = bears_col.find_one({"_id":objid})
        parent_f = buginfo["parent_id"]
        filepath=parent_f.split('@')[0]
        filename=filepath.split('\\')[-1]
        print(filepath)
        print(filename)
        data_json_f=filepath.replace("bears_data","bears_data_info")
        data_json_f=data_json_f.replace(filename,"data.json").replace("patch\\","")
        print(data_json_f)
        info_dict=json.load(codecs.open(data_json_f,'r',encoding='utf8'))
        bugid=info_dict["id"]
        javapaths=info_dict["java_paths"]
        if bugid in benchmark_dict.keys():
            new_dict=benchmark_dict[bugid]
            id_path=''
            for path in javapaths:
                if filename in path:
                    id_path=path
            new_dict[id]={"file_path":id_path,"buggy_method":codecs.open(buggy_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip(),
                          "fix_method":codecs.open(fix_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip(),
                          "classcontent":codecs.open(filepath,'r',encoding='utf8').read()}

            benchmark_dict[bugid]=infodict
        else:
            id_path=''
            for path in javapaths:
                if filename in path:
                    id_path=path

            infodict={id:{"file_path":id_path,"buggy_method":codecs.open(buggy_methods_dir+'/'+id+'.txt','r',encoding='utf8').read().strip(),
                          "fix_method": codecs.open(fix_methods_dir + '/' + id + '.txt', 'r',
                                                    encoding='utf8').read().strip(),
                          "classcontent":codecs.open(filepath,'r',encoding='utf8').read()}}
            benchmark_dict[bugid]=infodict
    with open(target_f,'w',encoding='utf8')as tf:
        json.dump(benchmark_dict,tf,indent=2)

def rewrite_Edits(benchmark_dir,edits_f,output_f):
    bears_ids=readF2L(benchmark_dir+'/bears.ids')
    qbs_ids=readF2L(benchmark_dir+'/qbs.ids')
    bdjar_ids=readF2L(benchmark_dir+'/bdjar.ids')
    d4j_ids=readF2L(benchmark_dir+'/d4j.ids')
    patches=json.load(codecs.open(edits_f,'r',encoding='utf8'))
    final_dict=dict()
    for id in patches.keys():
        content=patches.get(id)
        if id in bears_ids:
            id="bears_"+id
        if id in d4j_ids:
            id='d4j_'+id
        if id in qbs_ids:
            id='qbs_'+id
        if id in bdjar_ids:
            id='bdjar_'+id
        final_dict[id]=content
    with open(output_f,'w',encoding='utf8')as of:
        json.dump(final_dict,of)
        of.close()

def count_benchmarks(b_f):
    infos=json.load(codecs.open(b_f,'r',encoding='utf8'))
    print(len(infos.keys()))

def combine_ensemble_results(ids_f,paths,output_f):
    ids=readF2L(ids_f)
    dicts=[]
    final_dict= {}
    for path in paths:
        dict=json.load(codecs.open(path,'r',encoding='utf8'))
        dicts.append(dict)
    for id in ids:

        results=[]
        for dict in dicts:
            if id in dict.keys():
                results.append(int(dict.get(id)))
        print(id,results)
        if len(results)==0:
            final_dict[id] = -1
        elif sum(results)//len(results)==-1:
            final_dict[id]=-1
        else:
            hit_sum=[]
            for ind in results:
                if not ind==-1:
                    hit_sum.append(ind)
            final_dict[id]=sum(hit_sum)//len(hit_sum)
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)
def Recovery_Edits_Bears(patches_f,ids_f,benchmark_dir,output_f):
    ids=readF2L(ids_f)
    bears_patches=json.load(codecs.open(patches_f,'r',encoding='utf8'))
    final_dict={}
    for key in bears_patches.keys():
        ind=int(key)
        id='bears_'+ids[ind]
        buggy_method_f=benchmark_dir+'/buggy_methods/'+id+'.txt'
        buggy_line_f=benchmark_dir+'/buggy_lines/'+id+'.txt'
        if os.path.exists(buggy_method_f) and os.path.exists(buggy_line_f):
            buggy_method=codecs.open(buggy_method_f,'r',encoding='utf8').read().strip()
            buggy_line=codecs.open(buggy_line_f,'r',encoding='utf8').read().strip()
            candidates=bears_patches[key]["patches"]

            recover_candidates={}
            for cid in candidates.keys():
                candi=candidates.get(cid).replace('\t',' ')
                if buggy_line in buggy_method:
                    print("in")
                else:
                    print("not in")
                rec_method=buggy_method.replace(buggy_line," "+candi+" ")
                recover_candidates[cid]=rec_method
            final_dict[id]={"match_result":bears_patches[key]["match_result"],"patches":recover_candidates}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)

#Recovery_Edits_Bears(r"F:\NPR_DATA0306\FixResults\Final_Results\Bears.patches",r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.sids",
                     #"F:/NPR_DATA0306/Evaluationdata/Benchmark",r"F:\NPR_DATA0306\FixResults\Final_Results\Edits_bears.patches")

def write_trn_lines(dir,output_f):
    files=os.listdir(dir)
    lines=[]
    for file in files:
        buggy_line=codecs.open(dir+'/'+file,'r',encoding='utf8').read().strip()
        lines.append(buggy_line)
    writeL2F(lines,output_f)


d4j_bugs=json.load(codecs.open(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\infos.json",'r',encoding='utf8'))
all=d4j_bugs['d4j']
all_bugs=list(all.keys())

all_bugs.sort()
for bug in all_bugs:
    continue
    print(bug)

qbs_bugs=json.load(codecs.open(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\QuixBugs.json",'r',encoding='utf8'))
for bug in qbs_bugs.keys():

    print(qbs_bugs[bug]["name"])
#write_trn_lines("F:/NPR_DATA0306/train/buggy_lines","F:/NPR_DATA0306/train/train_lines.buggy")

#count_benchmarks(r"F:\NPR_DATA0306\Evaluationdata\Benchmark\Bdjar.json")
#rewrite_Edits("F:/NPR_DATA0306/Evaluationdata/Benchmark",r"F:\NPR_DATA0306\FixResults\Final_Results\Edit_benchmark.patches",)

#writeBeras_f("F:/NPR_DATA0306/Evaluationdata/Benchmark/benchmark.ids","F:/NPR_DATA0306/Evaluationdata/Benchmark/buggy_methods","F:/NPR_DATA0306/Evaluationdata/Benchmark/fix_methods","F:/NPR_DATA0306/Evaluationdata/Benchmark/Bears.json")

#prepare_diversity4edits("F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/final.ids","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/SequenceR")
#combine_SR("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/SequenceR",'buggy')
#combine_SR("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/SequenceR",'fix')
#combine_SR("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/SequenceR",'sids')
#combine_Tufano("F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/srcabs","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/for_Tufano/tgtabs",
#               "F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Tufano/diversity_")
#combine_Tufano("F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/srcabs","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/for_Tufano/tgtabs",
               #"F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/Tufano_bears")
#count_one_method_fix(["F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/father_dict_0_5k.json","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/father_dict_5k_1w.json",
#                      "F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/father_dict_1w_15k.json","F:/NPR_DATA0306/Evaluationdata/Diversity-processed/Recoder/father_dict_15k_after.json"])