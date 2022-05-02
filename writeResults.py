import codecs
import json
from Utils.IOHelper import readF2L
def writeSR(eval_dict_f,ids_f,patches_dir,output_f):
    eval_resutls=json.load(codecs.open(eval_dict_f,'r',encoding='utf8'))
    ids=readF2L(ids_f)
    final_dict=dict()
    for id in ids:
        objid=id
        str_match=eval_resutls[objid]
        patches=json.load(codecs.open(patches_dir+'/'+objid+'.fix','r',encoding='utf8'))
        patches_dict=dict()
        for key in patches.keys():
            patch='\n'.join(patches.get(key))
            #print(patch)
            patches_dict[key]=patch
        final_dict["bears_"+id]={"match_result":str_match,"patches":patches_dict}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)

def writeTufano(eval_dict_f,ids_f,patches_f,candi_size,output_f):
    eval_results=json.load(codecs.open(eval_dict_f,'r',encoding='utf8'))
    ids=readF2L(ids_f)
    patches=readF2L(patches_f)
    print(len(ids))
    print(len(patches))
    assert len(ids)*candi_size == len(patches)
    final_dict={}
    for i,id in enumerate(ids):

        str_match=eval_results[id]
        patches_perid=patches[i*candi_size:(i+1)*candi_size]
        patches_dict=dict()
        for idx,patch in enumerate(patches_perid):
            patches_dict[str(idx)]=patch
        final_dict[id]={"match_result":str_match,"patches":patches_dict}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)

def writeCoCoNut(eval_dict_f,ids_f,patches_dir,output_f):
    eval_resutls=json.load(codecs.open(eval_dict_f,'r',encoding='utf8'))
    ids=readF2L(ids_f)
    final_dict=dict()
    for id in ids:
        if id in eval_resutls.keys():
            str_match=eval_resutls[id]
            patches=json.load(codecs.open(patches_dir+'/'+id+'.txt','r',encoding='utf8'))
            patches_dict=dict()
            for key in patches.keys():
                patch=patches.get(key)
                #print(patch)
                patches_dict[key]=patch
            final_dict[id]={"match_result":str_match,"patches":patches_dict}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)

def writeRecoder(eval_dict_f,ids_f,patches_dir,output_f):
    eval_results = json.load(codecs.open(eval_dict_f, 'r', encoding='utf8'))
    ids=readF2L(ids_f)
    final_dict={}
    print(ids)
    for i,id in enumerate(ids):

        if id not in eval_results.keys():
            continue
        print(id)
        str_match = eval_results[id]
        candidates=json.load(codecs.open(patches_dir+'/'+id+'.fix', 'r', encoding='utf8'))
        final_dict[id] = {"match_result": str_match, "patches": candidates}
    with open(output_f,'w',encoding='utf8')as f:
        json.dump(final_dict,f,indent=2)


writeSR(eval_dict_f=r"F:\NPR_DATA0306\Bears_pred\SequenceR\SR_26_bears.eval",ids_f=r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\SequenceR\Bears.sids",
        patches_dir="F:/NPR_DATA0306/Bears_pred/SequenceR",output_f="F:/NPR_DATA0306/FixResults/Final_Results/SequenceR_Bears.patches")
#writeRecoder(eval_dict_f="F:/NPR_DATA0306/Recoder_new/bench_/recoder_eval.txt",ids_f="F:/NPR_DATA0306/Evaluationdata/Benchmark/Benchmark.ids",
             #patches_dir="F:/NPR_DATA0306/Recoder_new/bench_",output_f="F:/NPR_DATA0306/FixResults/Final_Results/Recoder_Benchmark.patches")

#writeTufano(eval_dict_f=r"F:\NPR_DATA0306\Bears_pred\Tufano\Tufano_bears_b100.eval",ids_f=r"F:\NPR_DATA0306\Evaluationdata\Benchmark-processed\Tufano_bears.ids",
        #patches_f=r"F:\NPR_DATA0306\Bears_pred\Tufano\Tufano_bears_b100.recovery",candi_size=100,output_f="F:/NPR_DATA0306/FixResults/Final_Results/Tufano_Bears.patches")
"""
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_5_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_5_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_5_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_12_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_12_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_12_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_15_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_15_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_15_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_21_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_21_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_21_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_32_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_32_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_32_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_33_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_33_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_33_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_35_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_35_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_35_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_99_save/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_99_save","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_99_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_context_tune_7/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_context_tune_7","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_c7_Bears.patches")
writeCoCoNut("F:/NPR_DATA0306/Bears_pred/CoCoNut_context_tune_9/pred_bears.eval","F:/NPR_DATA0306/Evaluationdata/Benchmark-processed/CoCoNut/Bears.ids",
             "F:/NPR_DATA0306/Bears_pred/CoCoNut_context_tune_9","F:/NPR_DATA0306/FixResults/Final_Results/CoCoNut_c9_Bears.patches")
"""
