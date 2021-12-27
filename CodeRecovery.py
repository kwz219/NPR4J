from Utils.IOHelper import readF2L


def Recovery_Tufano(ids_f,map_dir,preds_f,nbest=10):
    ids=readF2L(ids_f)
    n_preds=readF2L(preds_f)
    assert  len(ids)==len(n_preds)
    for i,id in enumerate(ids):
