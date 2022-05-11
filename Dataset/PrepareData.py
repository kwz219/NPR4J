import codecs
import os
import re

from bson import ObjectId

from Dataset.MongoHelper import MongoHelper
from Utils.IOHelper import readF2L, writeL2F
from Utils._tokenize import CoCoNut_tokenize
import shutil

def Tokenize_CoCoNut(src_file,output_file):
    src_lines=readF2L(src_file)
    toked_lines=[]
    for i,line in enumerate(src_lines):
        toked_lines.append(' '.join(CoCoNut_tokenize(line.strip())))
        print(i)
    writeL2F(toked_lines,output_file)
def prepare_test4CoCoNut(id_file,benchmark_dir,output_dir,prefix):
    buggy_methods_dir=benchmark_dir+'/buggy_methods/'
    buggy_lines_dir=benchmark_dir+"/buggy_lines/"
    fix_lines_dir=benchmark_dir+"/fix_lines/"
    benchmark_ids=[]
    buggy_ctxes=[]
    fix_lines=[]
    ids=readF2L(id_file)
    for id in ids:
        #print(id)
        #print(buggy_methods_dir+id)
        id='bears_'+id+'.txt'
        buggy_method=codecs.open(buggy_methods_dir+id,'r',encoding='utf8').read()
        buggy_method = re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)|(?://.*)", "", buggy_method)
        buggy_method = re.sub('\s+', ' ', buggy_method)
        buggy_line=codecs.open(buggy_lines_dir+id,'r',encoding='utf8').read().strip()
        fix_line=codecs.open(fix_lines_dir+id,'r',encoding='utf8').read().strip()
        toked_line = ' '.join(CoCoNut_tokenize(buggy_line.strip()))
        toked_ctx = ' '.join(CoCoNut_tokenize(buggy_method.replace('\n',' ').strip()))
        toked_fix = ' '.join(CoCoNut_tokenize(fix_line.strip()))
        buggy_ctxes.append(toked_line+' <CTX> '+toked_ctx)
        fix_lines.append(toked_fix)
        benchmark_ids.append(id.replace(".txt",''))
    writeL2F(buggy_ctxes,output_dir+'/'+prefix+'.ctx')
    writeL2F(fix_lines, output_dir + '/'+prefix+'.fix')
    writeL2F(benchmark_ids, output_dir + '/'+prefix+'.ids')

def prepare_CoCoNut(src_prefix,tgt_prefix):
    buggy_lines=readF2L(src_prefix+'.buggy')
    buggy_ctx=readF2L(src_prefix+'.buggy_ctx')
    fix_lines=readF2L(src_prefix+'.fix')
    assert len(buggy_lines)==len(fix_lines) and len(buggy_ctx)==len(fix_lines)
    toked_lines,toked_line_ctx,toked_fixes=[],[],[]
    i=0
    for line,ctx,fix in zip(buggy_lines,buggy_ctx,fix_lines):
        toked_line=' '.join(CoCoNut_tokenize(line.strip()))
        toked_ctx=' '.join(CoCoNut_tokenize(ctx.strip()))
        toked_fix=' '.join(CoCoNut_tokenize(fix.strip()))
        toked_lines.append(toked_line)
        toked_line_ctx.append(toked_line+' <CTX> '+toked_ctx)
        toked_fixes.append(toked_fix)
        print(i)
        i+=1
    writeL2F(toked_lines,tgt_prefix+'.buggy')
    writeL2F(toked_line_ctx, tgt_prefix + '.ctx')
    writeL2F(toked_fixes, tgt_prefix + '.fix')
def clean_CoCoNut(src_prefix):
    buggy_lines=readF2L(src_prefix+'.buggy')
    buggy_ctx=readF2L(src_prefix+'.ctx')
    fix_lines=readF2L(src_prefix+'.fix')
    metas=readF2L("F:/NPR_DATA0306/Large/trn.meta")
    clean_buggy,clean_fix,clean_ctx,clean_meta=[],[],[],[]
    for line, ctx, fix,meta in zip(buggy_lines, buggy_ctx, fix_lines,metas):
        if line != fix :
            tgt_len=len(line.split())
            if tgt_len>1000:
                print(tgt_len)
            #print(len(fix.split()))
            clean_buggy.append(line)
            clean_ctx.append(ctx)
            clean_fix.append(fix)
            clean_meta.append(meta)
    writeL2F(clean_buggy[2000:22100],src_prefix+'.clean.buggy')
    writeL2F(clean_ctx[2000:22100], src_prefix + '.clean.ctx')
    writeL2F(clean_fix[2000:22100], src_prefix + '.clean.fix')
    writeL2F(clean_meta[2000:22100], src_prefix + '.clean.meta')
def prepare_data(name,ids_f,output_dir,local_dir):
    ids=readF2L(ids_f)
    mongoClient = MongoHelper()
    bug_col=mongoClient.get_col("Buginfo")
    failed_ids=[]
    success_ids=[]
    os.makedirs(output_dir+'/buggy_methods')
    os.makedirs(output_dir + '/fix_methods')
    os.makedirs(output_dir + '/buggy_lines')
    os.makedirs(output_dir + '/fix_lines')
    os.makedirs(output_dir + '/buggy_classes')
    os.makedirs(output_dir + '/fix_classes')
    os.makedirs(output_dir + '/metas')
    for i,id in enumerate(ids):
        try:
            bug = bug_col.find_one({'_id': ObjectId(id)})
            id=str(bug['_id'])
            src_pos = bug['errs'][0]['src_pos']
            buggy_code=bug['buggy_code']
            fix_code=bug['fix_code']
            parent_id=bug['parent_id']
            parent_f=local_dir+'\\'+parent_id.split('@')[0]
            buggy_content = bug['errs'][0]['src_content'][0].strip()
            tgt_pos = bug['errs'][0]['tgt_pos']
            patch_content = bug['errs'][0]['tgt_content']
            oneline_patch = ''
            for content in patch_content:
                oneline_patch = oneline_patch + ' ' + content.strip() + ' '
            buggy_method_f = codecs.open(output_dir + '/buggy_methods/' + id + ".txt", 'w', encoding='utf8')
            buggy_method_f.write(buggy_code)
            buggy_method_f.close()
            fix_method_f = codecs.open(output_dir + '/fix_methods/' + id + ".txt", 'w', encoding='utf8')
            fix_method_f.write(fix_code)
            fix_method_f.close()

            buggy_line_f = codecs.open(output_dir + '/buggy_lines/' + id + ".txt", 'w', encoding='utf8')
            buggy_line_f.write(buggy_content)
            buggy_line_f.close()
            fix_line_f = codecs.open(output_dir + '/fix_lines/' + id + ".txt", 'w', encoding='utf8')
            fix_line_f.write(oneline_patch)
            fix_line_f.close()

            meta = name + '<sep>' + id + '<sep>' + src_pos + '<sep>' + tgt_pos + '<sep>' + parent_id
            meta_f = codecs.open(output_dir + '/metas/' + id + ".txt", 'w', encoding='utf8')
            meta_f.write(meta)
            meta_f.close()

            shutil.copy(parent_f,output_dir+'/buggy_classes/'+id+'.txt')
            shutil.copy(parent_f.replace("P_dir","F_dir"), output_dir + '/fix_classes/' + id + '.txt')
            success_ids.append(id)
        except:
            failed_ids.append(id)

        print(i)
    writeL2F(success_ids,output_dir+"/success.ids")
    writeL2F(failed_ids, output_dir + "/failed.ids")
prepare_data("data",r"F:\NPR_DATA0306\buggy_id_ahf.txt","F:/NPR_DATA0306/ahf_data",r"E:\\bug-fix")
def prepare_benchmark_4test(output_dir):
    mongoClient = MongoHelper()
    d4j_col=mongoClient.get_col("Binfo_d4j")
    bears_col = mongoClient.get_col("Binfo_Bears")
    bdj_col = mongoClient.get_col("Binfo_bdjar")
    qbs_col = mongoClient.get_col("Binfo_quixbugs")


    d4j_ids=[]
    bdjar_ids=[]
    bears_ids=[]
    qbs_ids=[]
    """
    for bug in d4j_col.find():
        id=str(bug['_id'])
        num_errs=str(bug['num_errs'])
        type_errs=bug['type_errs']
        buggy_code=bug['buggy_code']
        fix_code=bug['fix_code']
        parent_id=bug['parent_id']
        benchmark="d4j"
        if num_errs=='1' and type_errs=="replace":
            src_pos=bug['errs'][0]['src_pos']
            error_pos=str(src_pos).replace('[','').replace(']','').split(':')
            error_line=int(error_pos[1])-int(error_pos[0])
            if error_line==1:
                buggy_content=bug['errs'][0]['src_content'][0].strip()
                tgt_pos = bug['errs'][0]['tgt_pos']
                patch_content=bug['errs'][0]['tgt_content']
                oneline_patch=''
                for content in patch_content:
                    oneline_patch=oneline_patch+' '+content.strip()+' '
                buggy_method_f=codecs.open(output_dir+'/buggy_methods/d4j_'+id+".txt",'w',encoding='utf8')
                buggy_method_f.write(buggy_code)
                buggy_method_f.close()
                fix_method_f=codecs.open(output_dir+'/fix_methods/d4j_'+id+".txt",'w',encoding='utf8')
                fix_method_f.write(fix_code)
                fix_method_f.close()
                d4j_ids.append(id)
                buggy_line_f = codecs.open(output_dir + '/buggy_lines/d4j_' + id + ".txt", 'w', encoding='utf8')
                buggy_line_f.write(buggy_content)
                buggy_line_f.close()
                fix_line_f = codecs.open(output_dir + '/fix_lines/d4j_' + id + ".txt", 'w', encoding='utf8')
                fix_line_f.write(oneline_patch)
                fix_line_f.close()

                meta=benchmark+'<sep>'+id+'<sep>'+src_pos+'<sep>'+tgt_pos+'<sep>'+parent_id
                meta_f=codecs.open(output_dir+'/metas/d4j_'+id+ ".txt", 'w', encoding='utf8')
                meta_f.write(meta)
                meta_f.close()

    for bug in bdj_col.find():
        id = str(bug['_id'])
        num_errs = str(bug['num_errs'])
        type_errs = bug['type_errs']
        buggy_code = bug['buggy_code']
        fix_code = bug['fix_code']
        parent_id = bug['parent_id']
        benchmark = "bdjar"
        if num_errs == '1' and type_errs == "replace":
            src_pos = bug['errs'][0]['src_pos']
            error_pos = str(src_pos).replace('[', '').replace(']', '').split(':')
            error_line=int(error_pos[1])-int(error_pos[0])
            if error_line == 1:
                buggy_content = bug['errs'][0]['src_content'][0].strip()
                tgt_pos = bug['errs'][0]['tgt_pos']
                patch_content=bug['errs'][0]['tgt_content']
                oneline_patch = ''
                for content in patch_content:
                    oneline_patch = oneline_patch + ' ' + content.strip() + ' '
                buggy_method_f = codecs.open(output_dir + '/buggy_methods/bdjar_' + id + ".txt", 'w', encoding='utf8')
                buggy_method_f.write(buggy_code)
                buggy_method_f.close()
                fix_method_f = codecs.open(output_dir + '/fix_methods/bdjar_' + id + ".txt", 'w', encoding='utf8')
                fix_method_f.write(fix_code)
                fix_method_f.close()
                bdjar_ids.append(id)
                buggy_line_f = codecs.open(output_dir + '/buggy_lines/bdjar_' + id + ".txt", 'w', encoding='utf8')
                buggy_line_f.write(buggy_content)
                buggy_line_f.close()
                fix_line_f = codecs.open(output_dir + '/fix_lines/bdjar_' + id + ".txt", 'w', encoding='utf8')
                fix_line_f.write(oneline_patch)
                fix_line_f.close()

                meta = benchmark + '<sep>' + id + '<sep>' + src_pos + '<sep>' + tgt_pos + '<sep>' + parent_id
                meta_f = codecs.open(output_dir + '/metas/bdjar_' + id + ".txt", 'w', encoding='utf8')
                meta_f.write(meta)
                meta_f.close()
    """
    for bug in bears_col.find():
        id = str(bug['_id'])
        num_errs = str(bug['num_errs'])
        type_errs = bug['type_errs']
        buggy_code = bug['buggy_code']
        fix_code = bug['fix_code']
        parent_id = bug['parent_id']
        benchmark = "bears"
        if num_errs == '1' and type_errs == "replace":
            src_pos = bug['errs'][0]['src_pos']
            error_pos = str(src_pos).replace('[', '').replace(']', '').split(':')
            error_line=int(error_pos[1])-int(error_pos[0])
            if error_line == 1:
                buggy_content = bug['errs'][0]['src_content'][0].strip()
                tgt_pos = bug['errs'][0]['tgt_pos']
                patch_content=bug['errs'][0]['tgt_content']
                oneline_patch = ''
                for content in patch_content:
                    oneline_patch = oneline_patch + ' ' + content.strip() + ' '
                buggy_method_f = codecs.open(output_dir + '/buggy_methods/bears_' + id + ".txt", 'w', encoding='utf8')
                buggy_method_f.write(buggy_code)
                buggy_method_f.close()
                fix_method_f = codecs.open(output_dir + '/fix_methods/bears_' + id + ".txt", 'w', encoding='utf8')
                fix_method_f.write(fix_code)
                fix_method_f.close()
                bears_ids.append(id)
                buggy_line_f = codecs.open(output_dir + '/buggy_lines/bears_' + id + ".txt", 'w', encoding='utf8')
                buggy_line_f.write(buggy_content)
                buggy_line_f.close()
                fix_line_f = codecs.open(output_dir + '/fix_lines/bears_' + id + ".txt", 'w', encoding='utf8')
                fix_line_f.write(oneline_patch)
                fix_line_f.close()

                meta = benchmark + '<sep>' + id + '<sep>' + src_pos + '<sep>' + tgt_pos + '<sep>' + parent_id
                meta_f = codecs.open(output_dir + '/metas/bears_' + id + ".txt", 'w', encoding='utf8')
                meta_f.write(meta)
                meta_f.close()
    """
    for bug in qbs_col.find():
        id = str(bug['_id'])
        num_errs = str(bug['num_errs'])
        type_errs = bug['type_errs']
        buggy_code = bug['buggy_code']
        fix_code = bug['fix_code']
        parent_id = bug['parent_id']
        benchmark = "qbs"
        if num_errs == '1' and type_errs == "replace":
            src_pos = bug['errs'][0]['src_pos']
            error_pos = str(src_pos).replace('[', '').replace(']', '').split(':')
            error_line=int(error_pos[1])-int(error_pos[0])
            if error_line == 1:
                buggy_content = bug['errs'][0]['src_content'][0].strip()
                tgt_pos = bug['errs'][0]['tgt_pos']
                patch_content=bug['errs'][0]['tgt_content']
                oneline_patch = ''
                for content in patch_content:
                    oneline_patch = oneline_patch + ' ' + content.strip() + ' '
                buggy_method_f = codecs.open(output_dir + '/buggy_methods/qbs_' + id + ".txt", 'w', encoding='utf8')
                buggy_method_f.write(buggy_code)
                buggy_method_f.close()
                fix_method_f = codecs.open(output_dir + '/fix_methods/qbs_' + id + ".txt", 'w', encoding='utf8')
                fix_method_f.write(fix_code)
                fix_method_f.close()
                qbs_ids.append(id)
                buggy_line_f = codecs.open(output_dir + '/buggy_lines/qbs_' + id + ".txt", 'w', encoding='utf8')
                buggy_line_f.write(buggy_content)
                buggy_line_f.close()
                fix_line_f = codecs.open(output_dir + '/fix_lines/qbs_' + id + ".txt", 'w', encoding='utf8')
                fix_line_f.write(oneline_patch)
                fix_line_f.close()

                meta = benchmark + '<sep>' + id + '<sep>' + src_pos + '<sep>' + tgt_pos + '<sep>' + parent_id
                meta_f = codecs.open(output_dir + '/metas/qbs_' + id + ".txt", 'w', encoding='utf8')
                meta_f.write(meta)
                meta_f.close()
    writeL2F(d4j_ids,output_dir+"/d4j.ids")
    """
    writeL2F(bears_ids, output_dir + "/bears.ids")
    #writeL2F(bdjar_ids, output_dir + "/bdj.ids")
    #writeL2F(qbs_ids, output_dir + "/qbs.ids")
def get_sublist(src_prefix):
    buggy_ctx=readF2L(src_prefix+'.ctx')
    fix_lines=readF2L(src_prefix+'.fix')
    writeL2F(buggy_ctx[:47500],src_prefix+'_47500.ctx')
    writeL2F([fix.replace('\n', '').replace('\t', '') for fix in fix_lines[:47500]], src_prefix + '_47500.fix')
#Tokenize_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn.buggy","F:/NPR_DATA0306/Processed_CoCoNut/trn.buggy")
#Tokenize_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn.fix","F:/NPR_DATA0306/Processed_CoCoNut/trn.fix")
#prepare_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn","F:/NPR_DATA0306/Processed_CoCoNut/processed/trn")
#prepare_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/val","F:/NPR_DATA0306/Processed_CoCoNut/processed/val")
#clean_CoCoNut("F:/NPR_DATA0306/CoCoNut/trn")
#get_sublist("F:/NPR_DATA0306/CoCoNut/trn")
#prepare_benchmark_4test("F:/NPR_DATA0306/Evaluationdata/Benchmark")
#prepare_diversity_4test("F:/NPR_DATA0306/Evaluationdata/Diversity/test.ids","F:/NPR_DATA0306/Evaluationdata/Diversity")
#prepare_benchmark4CoCoNut("F:/NPR_DATA0306/Evaluationdata/Benchmark","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut")
#prepare_test4CoCoNut('F:/NPR_DATA0306/Evaluationdata/Benchmark/bears.ids','F:/NPR_DATA0306/Evaluationdata/Benchmark',"F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut","Bears")