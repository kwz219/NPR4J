#-*- coding : utf-8-*-
import codecs
import re

import javalang
import nltk
from bson import ObjectId

from CoCoNut.tokenization.tokenization import extract_strings, COMPOSED_SYMBOLS, camel_case_split, number_split, \
    remove_integer
from CodeAbstract.CA_src2abs import run_src2abs
from MongoHelper import MongoHelper
from DataConstants import BUG_COL,METHOD_COL
from CodeAbstract.CA_SequenceR import run_SequenceR_abs
#from CodeAbstract.CA_src2abs import run_src2abs
from Utils.IOHelper import writeL2F,readF2L
import os
from transformers import AutoTokenizer, GPT2Tokenizer


def shuffle(list1, list2, list3):
    assert len(list1) == len(list2) and len(list2) == len(list3)
    all = []
    for line1, line2, line3 in zip(list1, list2, list3):
        if len(line1.strip()) > 1 and len(line2.strip()) > 1:
            all.append(line1 + "<SEP>" + line2 + "<SEP>" + str(line3))
    import random
    random.shuffle(all)
    new_l1 = []
    new_l2 = []
    new_l3 = []
    for line in all:
        line1, line2, line3 = line.split('<SEP>')
        new_l1.append(line1)
        new_l2.append(line2)
        new_l3.append(line3)
    return new_l1, new_l2, new_l3
def preprocess_SequenceR(ids_f,method,input_dir,output_dir):
    ids=readF2L(ids_f)
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)

    if method=="SequenceR":
        def build(src_f, tgt_f, error_f, correct_f, ids):
            buggy_codes = []
            fix_codes = []
            error_ids = []
            correct_ids=[]
            ind=1
            newline_count=0
            in_count=0
            bug_1=0
            exist_count = 0
            not_exist = 0
            for id in ids:
                bug=bug_col.find_one({"_id":ObjectId(id)})
                if bug==None:
                    continue
                buggy_parent_f=bug['parent_id'].split("@")[0]
                tmp_f1="D:\DDPR_TEST\SR_AB\\val_tmp\\"+buggy_parent_f.split("\\")[0]+"_"+buggy_parent_f.split("\\")[-1]
                tmp_f2 = "D:\DDPR_TEST\SR_AB\\trn_tmp\\" + buggy_parent_f.split("\\")[0] + "_" + \
                         buggy_parent_f.split("\\")[-1]
                tmp_f3 = "D:\DDPR_TEST\SR_AB\\tmp\\" + buggy_parent_f.split("\\")[0] + "_" + \
                         buggy_parent_f.split("\\")[-1]
                if os.path.exists(tmp_f1):
                    tmp_f=tmp_f1
                    exist_count+=1
                elif os.path.exists(tmp_f2):
                    tmp_f=tmp_f2
                    exist_count += 1
                elif os.path.exists(tmp_f3):
                    tmp_f=tmp_f3
                    exist_count += 1
                else:
                    not_exist+=1
                    tmp_f=tmp_f1
                #print("exist",exist_count,"not_exist",not_exist)

                fix_code=''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()


                buggy_code,hitflag=run_SequenceR_abs(input_dir+buggy_parent_f,tmp_f,bug,max_length=1000)
                print("hitflag",hitflag)
                if len(buggy_code.strip())<=1:
                    hitflag=0
                if hitflag==1:
                    try:
                        toked_fix = javalang.tokenizer.tokenize(fix_code)
                        toked_fix = ' '.join([tok.value for tok in toked_fix])
                    except:
                        toked_fix = re.split(r"[.,!?;(){}]", fix_code)
                        toked_fix = ' '.join(toked_fix)
                    try:
                        toked_bug=javalang.tokenizer.tokenize(buggy_code)
                        toked_bug = ' '.join([tok.value for tok in toked_bug]).replace('< START_BUG >','<START_BUG>').replace('< END_BUG >','<END_BUG>')
                    except:
                        toked_bug = re.split(r"[.,!?;(){}]", buggy_code)
                        toked_bug = ' '.join(toked_bug).replace('< START_BUG >','<START_BUG>').replace('< END_BUG >','<END_BUG>')
                    bug_count=toked_bug.count('<START_BUG>'
                    )
                    if not bug_count==1:
                        bug_1+=1
                    else:
                        buggy_codes.append(toked_bug)
                        fix_codes.append(toked_fix)
                        if '\n' in toked_bug:
                            newline_count+=1
                            print("newline_count",newline_count)
                        #print(toked_bug)
                        #print(toked_fix)
                        correct_ids.append(bug['_id'])
                        in_count+=1
                elif hitflag==2:
                    print(tmp_f)
                else:
                    error_ids.append(bug['_id'])
                print(ind,"in:",in_count,"bug >1",bug_1)
                print("newline_count", newline_count)
                ind+=1
            assert len(buggy_codes)==len(fix_codes)
            buggy_codes,fix_codes,correct_ids=shuffle(buggy_codes,fix_codes,correct_ids)
            assert len(buggy_codes) == len(fix_codes)
            print(len(buggy_codes),len(fix_codes))
            print("newline_count", newline_count)
            writeL2F(buggy_codes,src_f)
            writeL2F(fix_codes,tgt_f)
            writeL2F(error_ids,error_f)
            writeL2F(correct_ids, correct_f)
        #build(output_dir+"trn.buggy",output_dir+"trn.fix",output_dir+"trn.fids",output_dir+"trn.sids",ids)
        build(output_dir+"trn.buggy",output_dir+"trn.fix",output_dir+"trn.fids",output_dir+"trn.sids",ids)
def preprocess_CoCoNut(ids_f,output_dir,prefix,max_length=1000):
    print("CoCoNut-Style data preprocess start ")
    def CoCoNut_tokenize(string):

        final_token_list = []
        string_replaced = extract_strings(string)
        split_tokens = re.split(r'([\W_])', string_replaced)
        split_tokens = list(filter(lambda a: a not in [' ', '', '"', "'", '\t', '\n'], split_tokens))
        flag = False

        # Special symbols
        for idx, token in enumerate(split_tokens):
            if idx < len(split_tokens) - 1:
                reconstructed_token = token + split_tokens[idx + 1]
                if reconstructed_token in COMPOSED_SYMBOLS:
                    final_token_list.append(reconstructed_token)
                    flag = True
                elif not flag:
                    final_token_list.append(token)
                elif flag:
                    flag = False
            else:
                final_token_list.append(token)
        # Camel Case
        no_camel = []
        for token in final_token_list:
            camel_tokens = camel_case_split(token)
            for idx, camel_tok in enumerate(camel_tokens):
                no_camel.append(camel_tok)

        # number split
        tokens = []
        for token in no_camel:
            number_sep = number_split(token)
            for num in number_sep:
                tokens.append(num)
        tokens = remove_integer(tokens)
        for idx, token in enumerate(tokens):
            if token == 'SSSTRINGSS':
                if idx > 0 and tokens[idx - 1] == '$STRING$':
                    return []
                else:
                    tokens[idx] = '$STRING$'

        return tokens
    ids=readF2L(ids_f)
    print(len(ids))
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)
    ind=0
    add_f=codecs.open(output_dir+'/'+prefix+'.fix','w',encoding='utf8')
    contex_f=codecs.open(output_dir+'/'+prefix+'.buggy','w',encoding='utf8')
    id_f=codecs.open(output_dir+'/'+prefix+".ids",'w',encoding='utf8')
    contex_fail=0
    for id in ids:
        bug = bug_col.find_one({"_id": ObjectId(id)})
        if bug == None:
            continue
        buggy_context=bug['buggy_code']
        remove_code=''.join([l.strip() for l in bug['errs'][0]['src_content']]).strip()
        fix_code = ''.join([l.strip() for l in bug['errs'][0]['tgt_content']]).strip()
        toked_rem=CoCoNut_tokenize(remove_code)
        contex_list=CoCoNut_tokenize(buggy_context)
        if len(contex_list)==0:
            rem_contex=toked_rem+["<CTX>"]+toked_rem
        else:
            rem_contex = toked_rem + ["<CTX>"] + contex_list


        if len(rem_contex)<max_length:
            add=CoCoNut_tokenize(fix_code)
            add_line=' '.join(add).replace('\n', '').replace('\t', '')
            context_line=' '.join(rem_contex).replace('\n', '').replace('\t', '')
            try:
                add_f.write(add_line+'\n')
                contex_f.write(context_line+'\n')
                id_f.write(id+'\n')
                pass
            except:
                pass

        ind+=1


    #writeL2F(add_lines,output_dir+'/'+prefix+'.fix')
    #writeL2F(remContext_lines,output_dir+'/'+prefix+'.buggy')
    #writeL2F(true_ids,output_dir+'/'+prefix+".ids")

def preprocess_Cure(ids_f,output_dir,prefix,max_length=2000):
    print("Cure-Style data preprocess start ")
    tokenizer=AutoTokenizer.from_pretrained("microsoft/CodeGPT-small-java")

    special_tokens=['CaMeL','$NUMBER$','$STRING$']
    tokenizer.add_tokens(special_tokens)

    def New_Cure_tokenize(string):
        final_token_list = []
        string_replaced = extract_strings(string)

        split_tokens = re.split(r'([\W_])', string_replaced)

        split_tokens = list(filter(lambda a: a not in ['', '"', "'", '\t', '\n'], split_tokens))
        flag = False

        # Special symbols
        for idx, token in enumerate(split_tokens):
            if idx < len(split_tokens) - 1:
                reconstructed_token = token + split_tokens[idx + 1]
                if reconstructed_token in COMPOSED_SYMBOLS:
                    final_token_list.append(reconstructed_token)
                    flag = True
                elif not flag:
                    final_token_list.append(token)
                elif flag:
                    flag = False
            else:
                final_token_list.append(token)
        # Camel Case
        no_camel = []
        for token in final_token_list:
            camel_tokens = camel_case_split(token)
            for idx, camel_tok in enumerate(camel_tokens):
                no_camel.append(camel_tok)

        # number split
        tokens = []
        for token in no_camel:
            number_sep = number_split(token)
            for num in number_sep:
                tokens.append(num)
        tokens = remove_integer(tokens)
        for idx, token in enumerate(tokens):
            if token == 'SSSTRINGSS':
                if idx > 0 and tokens[idx - 1] == '$STRING$':
                    return []
                else:
                    tokens[idx] = '$STRING$'
        line = ''.join(tokens)
        finalline = re.sub('\s+', ' ', line)
        return finalline

    ids=readF2L(ids_f)
    print(len(ids))
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)

    add_f=codecs.open(output_dir+'/'+prefix+'.fix','w',encoding='utf8')
    contex_f=codecs.open(output_dir+'/'+prefix+'.buggy','w',encoding='utf8')
    id_f=codecs.open(output_dir+'/'+prefix+".ids",'w',encoding='utf8')
    def get_types(context,bug):
        step=len(bug)
        bugtypes=["1" for i in range(len(bug))]
        index=0
        for i in range(0,len(context)-step):
            if context[i:i+step]==bug:
                index=i
                break
        types=["0" for i in range(index)]+bugtypes+["0" for i in range(len(context)-step-index)]
        #print(len(types),len(context))
        assert len(types)==len(context)

        return types
    ind=0
    for id in ids:
        bug = bug_col.find_one({"_id": ObjectId(id)})
        if bug == None:
            continue
        try:
            buggy_context = bug['buggy_code']
            remove_code = ''.join([l for l in bug['errs'][0]['src_content']])
            fix_code = ''.join([l for l in bug['errs'][0]['tgt_content']])
            CoNut_buggy_context=New_Cure_tokenize(buggy_context)
            CoNut_rem_code=New_Cure_tokenize(remove_code)
            CoNut_fix_code=New_Cure_tokenize(fix_code)
            GPT_buggy_context=tokenizer.tokenize(CoNut_buggy_context)
            GPT_rem_code=tokenizer.tokenize(CoNut_rem_code)
            GPT_fix_code=tokenizer.tokenize(CoNut_fix_code)
            ctx_types=get_types(GPT_buggy_context,GPT_rem_code)
            add_f.write(' '.join(GPT_fix_code)+'\n')
            contex_f.write(' '.join(GPT_buggy_context)+"<SEP>"+' '.join(ctx_types)+'\n')
            id_f.write(id+'\n')
        except:
            pass
        print(ind)
        ind+=1

def preprocess_Cure2(ids_f,output_dir,prefix,max_length=2000):
    print("Cure-Style data preprocess start ")
    tokenizer=AutoTokenizer.from_pretrained("microsoft/CodeGPT-small-java")

    special_tokens=['CaMeL','$NUMBER$','$STRING$']
    tokenizer.add_tokens(special_tokens)

    def New_Cure_tokenize(string):
        final_token_list = []
        string_replaced = extract_strings(string)

        split_tokens = re.split(r'([\W_])', string_replaced)

        split_tokens = list(filter(lambda a: a not in ['', '"', "'", '\t', '\n'], split_tokens))
        flag = False

        # Special symbols
        for idx, token in enumerate(split_tokens):
            if idx < len(split_tokens) - 1:
                reconstructed_token = token + split_tokens[idx + 1]
                if reconstructed_token in COMPOSED_SYMBOLS:
                    final_token_list.append(reconstructed_token)
                    flag = True
                elif not flag:
                    final_token_list.append(token)
                elif flag:
                    flag = False
            else:
                final_token_list.append(token)
        # Camel Case
        no_camel = []
        for token in final_token_list:
            camel_tokens = camel_case_split(token)
            for idx, camel_tok in enumerate(camel_tokens):
                no_camel.append(camel_tok)

        # number split
        tokens = []
        for token in no_camel:
            number_sep = number_split(token)
            for num in number_sep:
                tokens.append(num)
        tokens = remove_integer(tokens)
        for idx, token in enumerate(tokens):
            if token == 'SSSTRINGSS':
                if idx > 0 and tokens[idx - 1] == '$STRING$':
                    return []
                else:
                    tokens[idx] = '$STRING$'
        line = ''.join(tokens)
        finalline = re.sub('\s+', ' ', line)
        return finalline

    ids=readF2L(ids_f)
    print(len(ids))
    mongoClient=MongoHelper()
    bug_col=mongoClient.get_col(BUG_COL)

    add_f=codecs.open(output_dir+'/'+prefix+'.fix','w',encoding='utf8')
    contex_f=codecs.open(output_dir+'/'+prefix+'.buggy','w',encoding='utf8')
    id_f=codecs.open(output_dir+'/'+prefix+".ids",'w',encoding='utf8')

    ind=0
    for id in ids:
        bug = bug_col.find_one({"_id": ObjectId(id)})
        if bug == None:
            continue
        try:
            buggy_context = bug['buggy_code']
            remove_code = ''.join([l for l in bug['errs'][0]['src_content']])
            fix_code = ''.join([l for l in bug['errs'][0]['tgt_content']])
            CoNut_buggy_context=New_Cure_tokenize(buggy_context)
            CoNut_rem_code=New_Cure_tokenize(remove_code)
            CoNut_fix_code=New_Cure_tokenize(fix_code)
            GPT_buggy_context=tokenizer.tokenize(CoNut_buggy_context)
            GPT_rem_code=tokenizer.tokenize(CoNut_rem_code)
            GPT_fix_code=tokenizer.tokenize(CoNut_fix_code)

            add_f.write(' '.join(GPT_fix_code)+'\n')
            contex_f.write(' '.join(GPT_rem_code)+"<CTX>"+' '.join(GPT_buggy_context)+'\n')
            id_f.write(id+'\n')
        except:
            pass
        print(ind)
        ind+=1

def preprocess_Cure_fromCoCoNut(input_dir,out_dir):
    tokenizer=AutoTokenizer.from_pretrained("microsoft/CodeGPT-small-java")
    tokenizer.add_tokens(['CaMeL','<CTX>','$NUMBER$','$STRING$'])
    subnames=['val','test','trn']

    for subname in subnames:
        buggy_f=input_dir+'/'+subname+'.buggy'
        fix_f=input_dir+'/'+subname+'.fix'
        out_buggyf=codecs.open(out_dir+'/'+subname+'.buggy','w',encoding='utf8')
        out_fixf=codecs.open(out_dir+'/'+subname+'.fix','w',encoding='utf8')
        #blines=codecs.open(buggy_f,'r',encoding='utf8').readlines()
        flines=codecs.open(fix_f,'r',encoding='utf8').readlines()
        blines=readF2L(buggy_f)
        print(len(blines),len(flines))
        assert len(blines)==len(flines)
        ind=0
        for bline,fline in zip(blines,flines):
            toked_bline=tokenizer.tokenize(bline.strip())
            toked_fline=tokenizer.tokenize(fline.strip())
            out_buggyf.write(' '.join(toked_bline)+'\n')
            out_fixf.write(' '.join(toked_fline)+'\n')
            print(ind)
            ind+=1
        out_buggyf.close()
        out_fixf.close()


def preprocess_Tufano(ids_f,input_dir,output_dir,idom_path,raw_dir,name,max_length=1000):
    ids=readF2L(ids_f)
    buggy_codes = []
    fix_codes = []
    success_ids = []
    fail_ids = []
    ind=0
    for id in ids:
        out_a = input_dir + "/" + id + "_buggy.txt.abs"
        out_b = input_dir + "/" + id + "_fix.txt.abs"
        out_a2 = input_dir.replace('trn','test') + "/" + id + "_buggy.txt.abs"
        out_b2 = input_dir.replace('trn','test') + "/" + id + "_fix.txt.abs"
        #print(out_a)
        if os.path.exists(out_a) and os.path.exists(out_b):
            print("already exists 1")
            try:
                buggy_code=codecs.open(out_a,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b,'r',encoding='utf8').read()
                if buggy_code!=fix_code and 1<=len(buggy_code.split())<=max_length :
                    print('added')
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    success_ids.append(id)
            except:
                fail_ids.append(id)
        elif os.path.exists(out_a2) and os.path.exists(out_b2):
            print("already exists 2")
            try:
                buggy_code=codecs.open(out_a2,'r',encoding='utf8').read()
                fix_code=codecs.open(out_b2,'r',encoding='utf8').read()
                if buggy_code!=fix_code and len(buggy_code.split())<=max_length:
                    buggy_codes.append(buggy_code)
                    fix_codes.append(fix_code)
                    success_ids.append(id)
            except:
                fail_ids.append(id)
        else:
            print("generate abstraction of code")
            def find_f(candidate_dir):
                for dir in candidate_dir:
                    buggy_f=dir+'/'+id + "_buggy.txt"
                    fix_f=dir+'/'+id + "_fix.txt"
                    if os.path.exists(buggy_f) and os.path.exists(fix_f):
                        return buggy_f,fix_f
                return "error","error"
            buggy_f,fix_f=find_f([raw_dir])
            """
            if buggy_f=="error":
               bug = bug_col.find_one({"_id": ObjectId(id)})
               buggy_code=bug['buggy_code']
               fix_code=bug['fix_code']
               buggy_f=codecs.open(out_a,'w',encoding='utf8')
               fix_f = codecs.open(out_a, 'w', encoding='utf8')
               buggy_f.write(buggy_code)
               fix_f.write(fix_code)
               buggy_f.close()
               fix_f.close()
            """
            if buggy_f=="error":
                print("failed")
                fail_ids.append(id)
                continue
            run_src2abs("method",buggy_f,fix_f,out_a,out_b,idom_path)
            if os.path.exists(out_a) and os.path.exists(out_b):
                try:
                    buggy_code = codecs.open(out_a, 'r', encoding='utf8').read()
                    fix_code = codecs.open(out_b, 'r', encoding='utf8').read()
                    if buggy_code != fix_code and 1<=len(buggy_code.split()) <= max_length:
                        buggy_codes.append(buggy_code)
                        fix_codes.append(fix_code)
                        success_ids.append(id)
                except:
                    fail_ids.append(id)
        print(ind)
        ind+=1

    def shuffle(list1,list2,list3):
        assert  len(list1)==len(list2) and len(list2)==len(list3)
        all=[]
        for line1,line2,line3 in zip(list1,list2,list3):
            if len(line1.strip())>1 and len(line2.strip())>1:
                all.append(line1+"<SEP>"+line2+"<SEP>"+line3)
        import random
        random.shuffle(all)
        new_l1=[]
        new_l2=[]
        new_l3=[]
        for line in all:
            line1,line2,line3=line.split('<SEP>')
            new_l1.append(line1)
            new_l2.append(line2)
            new_l3.append(line3)
        return new_l1,new_l2,new_l3
    buggy_codes,fix_codes,success_ids=shuffle(buggy_codes,fix_codes,success_ids)
    writeL2F(buggy_codes,output_dir+"/"+name+".buggy")
    writeL2F(fix_codes, output_dir + "/" + name + ".fix")
    writeL2F(success_ids, output_dir + "/" + name + ".sids")
    writeL2F(fail_ids, output_dir + "/" + name + ".fids")





def test_preprocess():
    val_ids=readF2L("D:\DDPR\Dataset\\freq50_611\\val_ids.txt","D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut\\","val")
    #preprocess(val_ids,"SequenceR","E:\\bug-fix\\","D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")


#preprocess_Cure_fromCoCoNut("D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut","D:\DDPR_DATA\OneLine_Replacement\M1000_Cure")
#preprocess_Cure("D:\DDPR_DATA\OneLine_Replacement\Raw\\test_max1k.ids","D:\DDPR_DATA\OneLine_Replacement\M1000_Cure","test")
preprocess_Cure2("D:\DDPR_DATA\OneLine_Replacement\Raw\\trn_max1k.ids","D:\DDPR_DATA\OneLine_Replacement\Cure","trn")
preprocess_Cure2("D:\DDPR_DATA\OneLine_Replacement\Raw\\val_max1k.ids","D:\DDPR_DATA\OneLine_Replacement\Cure","val")
preprocess_Cure2("D:\DDPR_DATA\OneLine_Replacement\Raw\\test_max1k.ids","D:\DDPR_DATA\OneLine_Replacement\Cure","test")
#preprocess_CoCoNut("D:\DDPR\Dataset\\freq50_611\\val_ids.txt","D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut","val")
#preprocess_CoCoNut("D:\DDPR\Dataset\\freq50_611\\trn_ids.txt","D:\DDPR_DATA\OneLine_Replacement\M1000_CoCoNut","trn")
#preprocess_SequenceR("D:\DDPR\Dataset\\freq50_611\\trn_ids.txt","SequenceR","D:\DDPR_DATA\OneLine_Replacement\Raw\\trn","D:\DDPR_DATA\OneLine_Replacement\M1000_SequenceR\\")
#preprocess_Tufano("D:\DDPR\Dataset\\freq50_611\\test_ids.txt","E:\APR_data\data\Tufano\\test","D:\DDPR_DATA\OneLine_Replacement\M1000_Tufano","D:\DDPR\CodeAbstract\CA_Resource\idioms.10w","D:\DDPR_DATA\OneLine_Replacement\Raw\\val","val")