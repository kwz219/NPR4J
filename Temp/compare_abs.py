from Utils.IOHelper import readF2L


def compare_abs(tufano_abs,tufano_ids,sr_abs,sr_ids):
    tufano_codes=readF2L(tufano_abs)
    tufano_ids = readF2L(tufano_ids)
    sr_codes = readF2L(sr_abs)
    sr_ids = readF2L(sr_ids)
    for id in sr_ids:
        if id in tufano_ids :
            tufano_index=tufano_ids.index(id)
            sr_index=sr_ids.index(id)
            print(tufano_codes[tufano_index])
            print(sr_codes[sr_index])
            print("-------------------------------------")
compare_abs("D:\DDPR_DATA\OneLine_Replacement\M1000_Tufano\\trn.fix","D:\DDPR_DATA\OneLine_Replacement\M1000_Tufano\\trn.sids",
            "G:\DDPR_backup\OneLine_Replacement\M2L_Tufano2w\\trn.fix","G:\DDPR_backup\OneLine_Replacement\M2L_Tufano2w\\trn.ids")