import codecs
import random
import re

import javalang
from bson import ObjectId

from Dataset.DataConstants import BUG_COL
from Dataset.MongoHelper import MongoHelper
from Utils.IOHelper import writeL2F,readF2L

def count_diff():
    mongoClient = MongoHelper()
    bug_col = mongoClient.get_col(BUG_COL)
    diff_size=0
    replace_count=0
    i=0
    for bug in bug_col.find():
        #num_errs=int(bug['num_errs'])
        errs=bug['errs']
        diff_size+=len(errs)
        for err in errs:
            if err['type']=='replace':
                replace_count+=1
        print(i)
        i+=1
    print("replace",replace_count)
    print("diffsize",diff_size)

def get_Replace_diffs():
    mongoClient = MongoHelper()
    bug_col = mongoClient.get_col(BUG_COL)
    diff_size=0
    replace_count=0
    i=0
    diffs=[]
    def merge2line(content,type):
        new_line=''
        for line in content:
            line=line.strip()
            if len(line)>0 and (not str(line).startswith('/')):
                new_line=new_line+' '+line
        return new_line.strip()
    def count_codetokens(codeline):
        tokens=[]
        try:
            tokens=[tok.value for tok in javalang.tokenizer.tokenize(codeline)]
        except:
            tokens = re.split(r"[.,!?;(){}]", codeline)
        return len(tokens)
    for bug in bug_col.find():
        #num_errs=int(bug['num_errs'])
        errs=bug['errs']
        for err in errs:
            diff = []
            if err['type']=='replace':
                diff.append(str(bug['_id']))
                diff.append(str(bug['parent_id']).split('\\')[0])
                src_content=merge2line(err['src_content'],'src')
                tgt_content=merge2line(err['tgt_content'],'tgt')
                #print(src_content)
                #print(tgt_content)
                diff.append(src_content)
                diff.append(tgt_content)
                src_length=count_codetokens(src_content)
                tgt_length=count_codetokens(tgt_content)
                diff.append(str(err['src_pos']))
                diff.append(str(err['tgt_pos']))
                diff.append(str(src_length))
                diff.append(str(tgt_length))
                if src_length>0 and tgt_length>0:
                    diffs.append(str('<sep>'.join(diff)))
                    print(i)
                    i+=1
    def takesrclen(diff):
        infos=diff.split("<sep>")
        srclen=int(infos[6])
        tgtlen=int(infos[7])
        return srclen+tgtlen
    diffs.sort(key=takesrclen)
    writeL2F(diffs,"Replace_diffs2.txt")


def count_length(startind,endind):
    metas=readF2L("F:/NPR_DATA0306/Original/trn/meta.txt")
    lengths=[]
    for meta in metas[startind:endind]:
        src_len=int(meta.split('<sep>')[2])
        lengths.append(src_len)
    print(sum(lengths)/len(lengths))

def extract_trndata_4CoCoNut(startind,endind):
    buggylines=readF2L("F:/NPR_DATA0306/Original/trn/buggy.txt")
    metas = readF2L("F:/NPR_DATA0306/Original/trn/meta.txt")
    fixlines= readF2L("F:/NPR_DATA0306/Original/trn/fix.txt")
    assert len(buggylines)==len(metas) and len(metas)==len(fixlines)
    selected_buggylines=buggylines[startind:endind]
    selected_metas=metas[startind:endind]
    selected_fixlines=fixlines[startind:endind]
    trn_buggy_f=codecs.open("F:/NPR_DATA0306/CoCoNut/trn.buggy",'w',encoding='utf8')
    trn_fix_f = codecs.open("F:/NPR_DATA0306/CoCoNut/trn.fix", 'w', encoding='utf8')
    trn_meta_f = codecs.open("F:/NPR_DATA0306/CoCoNut/trn.meta", 'w', encoding='utf8')
    for b,f,m in zip(selected_buggylines,selected_fixlines,selected_metas):
        trn_buggy_f.write(b+'\n')
        trn_fix_f.write(f+'\n')
        trn_meta_f.write(m+'\n')
    trn_buggy_f.close()
    trn_fix_f.close()
    trn_meta_f.close()
def extract_testdata_4CoCoNut(startind,endind):
    buggylines=readF2L("F:/NPR_DATA0306/Original/OneLine_Patch/buggy.txt")
    metas = readF2L("F:/NPR_DATA0306/Original/OneLine_Patch/meta.txt")
    fixlines= readF2L("F:/NPR_DATA0306/Original/OneLine_Patch/fix.txt")
    assert len(buggylines)==len(metas) and len(metas)==len(fixlines)
    selected_buggylines=buggylines[startind:endind]
    selected_metas=metas[startind:endind]
    selected_fixlines=fixlines[startind:endind]
    test_buggy_f=codecs.open("F:/NPR_DATA0306/Large/test.buggy",'w',encoding='utf8')
    test_fix_f = codecs.open("F:/NPR_DATA0306/Large/test.fix", 'w', encoding='utf8')
    test_meta_f = codecs.open("F:/NPR_DATA0306/Large/test.meta", 'w', encoding='utf8')
    for b,f,m in zip(selected_buggylines,selected_fixlines,selected_metas):
        test_buggy_f.write(b+'\n')
        test_fix_f.write(f+'\n')
        test_meta_f.write(m+'\n')
    test_buggy_f.close()
    test_fix_f.close()
    test_meta_f.close()
def extract_ctx(metafile):
    metas=readF2L(metafile)
    mongoClient = MongoHelper()
    bugcol=mongoClient.get_col(BUG_COL)
    buggy_ctx=[]
    fix_ctx=[]
    for i,meta in enumerate(metas):
        id=meta.split('<sep>')[0]
        bug = bugcol.find_one({'_id': ObjectId(id)})
        buggy_code=bug['buggy_code']
        buggy_code = re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)|(?://.*)", "", buggy_code)
        buggy_code = re.sub('\s+', ' ', buggy_code)
        fix_code=bug['fix_code']
        fix_code = re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)|(?://.*)", "", fix_code)
        fix_code = re.sub('\s+', ' ', fix_code)
        buggy_ctx.append(buggy_code)
        fix_ctx.append(fix_code)
        print(i)
    assert len(buggy_ctx)==len(fix_ctx) and len(fix_ctx)==len(metas)
    writeL2F(buggy_ctx,"F:/NPR_DATA0306/Large/test.buggy_ctx")
    writeL2F(fix_ctx, "F:/NPR_DATA0306/Large/test.fix_ctx")

def extract_commits_4val(repofile):
    repo_infos=readF2L(repofile)
    commits4val=[]
    for info in repo_infos:
        infol=info.split('<sep>')
        count=int(infol[-1])
        if count<50:
           commits4val+=infol[1:count+1]
    writeL2F(commits4val,"Commits4val.txt")

def extract_valdata_4CoCoNut(testdir):
    commits4val=readF2L("Commits4val.txt")
    src_meta=readF2L(testdir+'/meta.txt')
    src_buggy=readF2L(testdir+'/buggy.txt')
    src_fix=readF2L(testdir+'/fix.txt')
    new_meta,new_buggy,new_fix=[],[],[]
    i=0
    for bug,fix,meta in zip(src_buggy,src_fix,src_meta):
        minfo=meta.split('<sep>')
        randomnum=random.random()
        #print(randomnum)
        if minfo[1] in commits4val and int(minfo[2])>=5 and int(minfo[2])<=200 and randomnum>=0.85:
            new_meta.append(meta)
            new_buggy.append(bug)
            new_fix.append(fix)
            print(i)
            i+=1
    writeL2F(new_meta,'F:/NPR_DATA0306/Large/val.meta')
    writeL2F(new_buggy, 'F:/NPR_DATA0306/Large/val.buggy')
    writeL2F(new_fix, 'F:/NPR_DATA0306/Large/val.fix')


def find_one_line_patch():
    repo_infos = readF2L("commits_special.txt")
    commits4test=[]
    commits_special=readF2L("repo&commits_special.txt")
    c_special=[]
    for info in commits_special:
        commit=info.split('<sep>')[0]
        c_special.append(commit)
    for info in repo_infos:
        infol = info.split('<sep>')
        count = int(infol[-1])
        if count >= 50:
            commits4test += infol[1:count + 1]
    test_metas=readF2L("F:/NPR_DATA0306/Original/test/meta.txt")
    test_buggy=readF2L("F:/NPR_DATA0306/Original/test/buggy.txt")
    test_fix=readF2L("F:/NPR_DATA0306/Original/test/fix.txt")
    change_count={}
    new_buggy=[]
    new_fix=[]
    new_meta=[]
    for meta in test_metas:
        infos=meta.split('<sep>')
        commit_sha=infos[1]
        if commit_sha in c_special:
            if commit_sha in change_count.keys():
                change_count[commit_sha]=change_count[commit_sha]+1
            else:
                change_count[commit_sha]=1
    i=0
    for bug,fix,meta in zip(test_buggy,test_fix,test_metas):
        infos=meta.split('<sep>')
        commit_sha=infos[1]
        if commit_sha in change_count.keys():
            if change_count[commit_sha]==1:
                new_buggy.append(bug)
                new_fix.append(fix)
                new_meta.append(meta)
                print(i)
                i+=1
    writeL2F(new_buggy,"F:/NPR_DATA0306/Original/OneLine_Patch/buggy.txt")
    writeL2F(new_fix, "F:/NPR_DATA0306/Original/OneLine_Patch/fix.txt")
    writeL2F(new_meta, "F:/NPR_DATA0306/Original/OneLine_Patch/meta.txt")

if __name__ == "__main__":
    #get_Replace_diffs()
    #count_length("split/trn/buggy.txt")
    #count_length("split/trn/fix.txt")

    #extract_trndata_4CoCoNut(100000,1170000)
    #extract_commits_4val("commits_special.txt")
    #extract_ctx("F:/NPR_DATA0306/Large/val.meta")
    #extract_valdata_4CoCoNut("F:/NPR_DATA0306/Large/test")
    extract_ctx("F:/NPR_DATA0306/Large/test.meta")
    #extract_testdata_4CoCoNut(700,23700)
    #find_one_line_patch()