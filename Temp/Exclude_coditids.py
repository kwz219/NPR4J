from Utils.IOHelper import readF2L, writeL2F


def exclude():
    ori_ids=readF2L("D:\\DDPR_DATA\\OneLine_Replacement\\Raw\\trn_max1k_f1-6.ids")
    trn_ids=readF2L("D:\DDPR_DATA\OneLine_Replacement\Codit_trn\\val\\files.txt")
    trn_ids2=readF2L("D:\DDPR_DATA\OneLine_Replacement\Codit_trn2\\val\\files.txt")
    trn_ids3 = readF2L("D:\DDPR_DATA\OneLine_Replacement\Codit_trn3\\val\\files.txt")
    trn_ids8 = readF2L("D:\DDPR_DATA\OneLine_Replacement\Codit_trn8\\val\\files.txt")
    def getids(ids):
        newids=[file.split('\\')[-1].replace('.buggy','') for file in ids]
        return newids
    exclude_ids=list(set(getids(trn_ids8)))
    filtered_ids=[]
    for id in ori_ids:
        if id not in exclude_ids:
            filtered_ids.append(id)
            print(len(filtered_ids))
    writeL2F(filtered_ids,"D:\\DDPR_DATA\\OneLine_Replacement\\Raw\\trn_max1k_f1-8.ids")

exclude()