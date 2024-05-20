from Utils.IOHelper import readF2L,writeL2F


def extract_idioms(ori_f,output_f):
    idioms=readF2L(ori_f)
    writeL2F(idioms[:40000],output_f)
extract_idioms("idioms.10w","idioms.4w")