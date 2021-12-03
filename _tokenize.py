from Utils.IOHelper import readF2L,writeL2F
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
if __name__ =="__main__":
    retokenize(src_f="D:\DDPR_TEST\SR_AB\\buggy.trn.txt",tgt_f="E:\APR_data\SequenceR\\buggy.trn.txt",tokenizetype="javalang")
    retokenize(src_f="D:\DDPR_TEST\SR_AB\\buggy.val.txt",tgt_f="E:\APR_data\SequenceR\\buggy.val.txt",tokenizetype="javalang")
    retokenize(src_f="D:\DDPR_TEST\SR_AB\\fix.trn.txt",tgt_f="E:\APR_data\SequenceR\\fix.trn.txt",tokenizetype="javalang")
    retokenize(src_f="D:\DDPR_TEST\SR_AB\\fix.val.txt",tgt_f="E:\APR_data\SequenceR\\fix.val.txt",tokenizetype="javalang")

