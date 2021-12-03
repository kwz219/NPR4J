from Tokenize.javalang_tokenizer import JavaLangTokenizer
from Utils.IOHelper import readF2L, writeL2F


def retokenize(src_f,tgt_f,tokenizetype):
    if tokenizetype=="javalang":
        tokenizer=JavaLangTokenizer()
    src_lines=readF2L(src_f)
    new_lines=[]
    for line in src_lines:
        print(line)
        new_line=' '.join(tokenizer.tokenize(line.strip()))
        new_lines.append(new_line)
    writeL2F(new_lines,tgt_f)

def retokenize_pair(tokenizetype,src_f,tgt_f,output_src_f,output_tgt_f,log_f,src_maxlen,tgt_maxlen):
    if tokenizetype=="javalang":
        tokenizer=JavaLangTokenizer()
    src_lines = readF2L(src_f)
    tgt_lines = readF2L(tgt_f)
    assert len(src_lines)==len(tgt_lines)
    tok_log=[]
    src_outputs=[]
    tgt_outputs=[]
    ind=1
    for src,tgt in zip(src_lines,tgt_lines):
        src=src.strip()
        tgt=tgt.strip()
        if len(src)==0 or len(tgt)==0:
            tok_log.append("Empty line")
        else:
            try:
                src_new = tokenizer.tokenize(src.strip())
                tgt_new = tokenizer.tokenize(tgt.strip())
                if len(src_new)>src_maxlen or len(tgt_new)>tgt_maxlen:
                    tok_log.append("Tokenize exceeds max length")
                elif len(src_new)==0 or len(tgt_new)==0:
                    tok_log.append("Empty line")
                else:
                    src_outputs.append(' '.join(src_new))
                    tgt_outputs.append(' '.join(tgt_new))
                    tok_log.append("Tokenize success")
            except:
                tok_log.append("Tokenize error")
        print(ind)
        ind+=1
    writeL2F(src_outputs,output_src_f)
    writeL2F(tgt_outputs,output_tgt_f)
    writeL2F(tok_log,log_f)
retokenize_pair(tokenizetype="javalang",
                src_f="D:\DDPR_TEST\SR_AB\\buggy.val.txt",
                tgt_f="D:\DDPR_TEST\SR_AB\\fix.val.txt",
                output_src_f="E:\APR_data\data\SequenceR\\buggy.val.txt",
                output_tgt_f="E:\APR_data\data\SequenceR\\fix.val.txt",
                log_f="E:\APR_data\data\SequenceR\\tok_log.val.txt",
                src_maxlen=1000,
                tgt_maxlen=100
                )
retokenize_pair(tokenizetype="javalang",
                src_f="D:\DDPR_TEST\SR_AB\\buggy.trn.txt",
                tgt_f="D:\DDPR_TEST\SR_AB\\fix.trn.txt",
                output_src_f="E:\APR_data\data\SequenceR\\buggy.trn.txt",
                output_tgt_f="E:\APR_data\data\SequenceR\\fix.trn.txt",
                log_f="E:\APR_data\data\SequenceR\\tok_log.trn.txt",
                src_maxlen=1000,
                tgt_maxlen=100
                )
