import javalang
from Utils.IOHelper import readF2L, writeL2F
from tokenizer import Tokenizer

class JavaLangTokenizer(Tokenizer):
    def __init__(self):
        self.tokenizer=javalang.tokenizer
    def tokenize(self,sentence):
        toked=self.tokenizer.tokenize(sentence,ignore_errors=True)
        toked=[tok.value for tok in toked]
        return toked
def retokenize(src_f,tgt_f,tokenizetype):
    if tokenizetype=="javalang":
        tokenizer=JavaLangTokenizer()
    src_lines=readF2L(src_f)
    new_lines=[]
    error_ids=[]
    ind=1
    for line in src_lines:
        try:
            new_line=' '.join(tokenizer.tokenize(line.strip()))
            new_lines.append(new_line)
        except:
            new_lines.append(line)
            error_ids.append(str(ind))
        print(ind)
        ind+=1

    writeL2F(error_ids,tgt_f+".err")
    writeL2F(new_lines,tgt_f)

def test():
    ex_inputs=readF2L("D:\DDPR\Tokenize\Example")
    jtokenizer=JavaLangTokenizer()
    for ex in ex_inputs:
        print(jtokenizer.tokenize(ex))
#retokenize(src_f="D:\DDPR_TEST\SR_AB\\buggy.trn.txt",tgt_f="E:\APR_data\SequenceR\\buggy.trn.txt",tokenizetype="javalang")
#retokenize(src_f="D:\DDPR_TEST\SR_AB\\buggy.val.txt",tgt_f="E:\APR_data\SequenceR\\buggy.val.txt",tokenizetype="javalang")
#retokenize(src_f="D:\DDPR_TEST\SR_AB\\fix.trn.txt",tgt_f="E:\APR_data\SequenceR\\fix.trn.txt",tokenizetype="javalang")
#retokenize(src_f="D:\DDPR_TEST\SR_AB\\fix.val.txt",tgt_f="E:\APR_data\SequenceR\\fix.val.txt",tokenizetype="javalang")