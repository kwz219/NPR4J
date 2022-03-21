from Utils.IOHelper import readF2L, writeL2F
from Utils._tokenize import CoCoNut_tokenize


def Tokenize_CoCoNut(src_file,output_file):
    src_lines=readF2L(src_file)
    toked_lines=[]
    for i,line in enumerate(src_lines):
        toked_lines.append(' '.join(CoCoNut_tokenize(line.strip())))
        print(i)
    writeL2F(toked_lines,output_file)
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

def get_sublist(src_prefix):
    buggy_ctx=readF2L(src_prefix+'.ctx')
    fix_lines=readF2L(src_prefix+'.fix')
    writeL2F(buggy_ctx[:47500],src_prefix+'_47500.ctx')
    writeL2F([fix.replace('\n', '').replace('\t', '') for fix in fix_lines[:47500]], src_prefix + '_47500.fix')
#Tokenize_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn.buggy","F:/NPR_DATA0306/Processed_CoCoNut/trn.buggy")
#Tokenize_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn.fix","F:/NPR_DATA0306/Processed_CoCoNut/trn.fix")
prepare_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/trn","F:/NPR_DATA0306/Processed_CoCoNut/processed/trn")
prepare_CoCoNut("F:/NPR_DATA0306/Processed_CoCoNut/val","F:/NPR_DATA0306/Processed_CoCoNut/processed/val")
#clean_CoCoNut("F:/NPR_DATA0306/CoCoNut/trn")
#get_sublist("F:/NPR_DATA0306/CoCoNut/trn")