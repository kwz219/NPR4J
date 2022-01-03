import codecs

from Utils.CA_Utils import writeL2F
from Utils.IOHelper import readF2L


def cut(buggy_f,fix_f,ids_f,out_dir,shards=5):
    buggy_codes=readF2L(buggy_f)
    fix_codes=readF2L(fix_f)
    ids=readF2L(ids_f)
    assert len(buggy_codes)==len(fix_codes) and len(fix_codes)==len(ids)
    step=len(ids)//shards

    for i in range(shards):
        b_shard=buggy_codes[i*step:(i+1)*step]
        f_shard = fix_codes[i * step:(i + 1) * step]
        id_shard = ids[i * step:(i + 1) * step]
        if i == (shards-1):
            b_shard = buggy_codes[i * step:]
            f_shard = fix_codes[i * step:]
            id_shard = ids[i * step:]

        writeL2F(b_shard,out_dir+'/test'+str(i)+'.buggy')
        writeL2F(f_shard, out_dir + '/test'+str(i)+'.fix')
        writeL2F(id_shard, out_dir + '/test'+str(i)+'.ids')
cut("D:\DDPR_DATA\OneLine_Replacement\Raw_M2M4BPE\\test.buggy","D:\DDPR_DATA\OneLine_Replacement\Raw_M2M4BPE\\test.fix","D:\DDPR_DATA\OneLine_Replacement\Raw_M2M4BPE\\test.ids","D:\DDPR_DATA\OneLine_Replacement\Raw_M2M4BPE\\test_dis")