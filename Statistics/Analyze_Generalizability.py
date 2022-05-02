import codecs
import json

import numpy as np
import pandas as pd

from Utils.IOHelper import readF2L

def get_candidates_num_analyze(diversity_f):
    diversity_result=codecs.open(diversity_f,'r',encoding='utf8')

    d_re=json.load(diversity_result)

    re_list=np.array(list(d_re.values()))
    series=pd.Series(re_list)
    check_range=list(range(0,100,5))
    statistics_dict=dict()
    statistics_dict["1"]=sum(re_list==0)
    for start in check_range:
        count=sum(series.between(0,start+4)==True)
        statistics_dict[str(start+5)]=count
    return statistics_dict
def calculate_area(num):
        if num==0:
            return '0'
        elif num>0 and num <=0.1:
            return '0.1'
        elif num>0.1 and num <=0.2:
            return '0.2'
        elif num>0.2 and num <=0.3:
            return '0.3'
        elif num>0.3 and num <=0.4:
            return '0.4'
        elif num>0.4 and num <=0.5:
            return '0.5'
        elif num>0.5 and num <=0.55:
            return '0.55'
        elif num>0.55 and num <=0.6:
            return '0.6'
        elif num>0.6 and num <=0.65:
            return '0.65'
        elif num>0.65 and num <=0.7:
            return '0.7'
        elif num>0.7 and num <=0.75:
            return '0.75'
        elif num>0.75 and num <=0.8:
            return '0.8'
        elif num>0.8 and num <=0.85:
            return '0.85'
        elif num>0.85 and num <=0.9:
            return '0.9'
        elif num>0.9 and num <=0.95:
            return '0.95'
        elif num>0.95 and num <1:
            return '1'
        else:
            return '1.0'
def analyze_generalizability():
    dis_dict={}
    dir="F:/NPR_DATA0306/Analyze/distance"
    files=["all.ids1","all.ids2","all.ids3","all.ids4","all.ids5","all.ids6"]
    for file in files:
        with open(dir+'/'+file,'r',encoding='utf8')as f:
            for line in f:
                infos=line.strip().split()
                dis_dict[infos[0]]=infos[1]
    hit_ids=readF2L(r"F:\NPR_DATA0306\Analyze\distance\correct.ids")
    sta4hit={}
    sta4fail={}
    all_dict={}
    print(len(dis_dict.keys()))
    for id in dis_dict.keys():
        #print(id)
        area = calculate_area(float(dis_dict[id]))
        if area in all_dict.keys():
            co = all_dict.get(area)
            co.append(id)
            all_dict.update({area: co})
        else:
            all_dict[area] = [id]
        if id in hit_ids:
            area=calculate_area(float(dis_dict[id]))
            if area in sta4hit.keys():
                co=sta4hit.get(area)
                co.append(id)
                sta4hit.update({area:co})
            else:
                sta4hit[area]=[id]
        else:
            area=calculate_area(float(dis_dict[id]))
            if area in sta4fail.keys():
                co=sta4fail.get(area)
                co.append(id)
                sta4fail.update({area:co})
            else:
                sta4fail[area]=[id]
    print(all_dict)
    #print(sum(all_dict.values()))
    with open(r"F:\NPR_DATA0306\Analyze\distance\area_dict.json",'w',encoding='utf8')as f:
        json.dump(all_dict,f,indent=2)
analyze_generalizability()
def analyze_distance():
    dis_dict={}
    dir="F:/NPR_DATA0306/Analyze/distance"
    files=["all.ids1","all.ids2","all.ids3","all.ids4","all.ids5","all.ids6"]
    for file in files:
        with open(dir+'/'+file,'r',encoding='utf8')as f:
            for line in f:
                infos=line.strip().split()
                dis_dict[infos[0]]=infos[1]
    CoCoNut_eval=json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\CoCoNut_union_diversity.eval"))
    Edits_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Edits_diversity.eval"))
    Recoder_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Recoder_new_diversity.eval"))
    SequenceR_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\SequenceR_diversity.eval"))
    Tufano_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Tufano_diversity.eval"))
    Codit_eval = json.load(codecs.open(r"F:\NPR_DATA0306\Eval_result\diversity\Codit_diversity.eval"))
    dict={"CoCoNut":CoCoNut_eval,"Edits":Edits_eval,"Recoder":Recoder_eval,"SequenceR":SequenceR_eval,"Tufano":Tufano_eval,"Codit":Codit_eval}
    hit_dict = {"CoCoNut": set(), "Edits": set(), "Recoder": set(), "SequenceR": set(),
            "Tufano": set(), "Codit": set()}
    area_dict=json.load(codecs.open(r"F:\NPR_DATA0306\Analyze\distance\area_dict.json",'r',encoding='utf8'))
    for key in dict.keys():
        sys_area_dict={}

        evals=dict.get(key)

        def get_area_sum(dict,area):
            sum=0
            if area not in dict.keys():
                return 0
            if area=='0':
                sum=len(dict['0'])
            elif area=='1.0':
                sum=len(dict['1.0'])
            else:
                for key in dict.keys():
                    if float(key) <= float(area) and not (key=="1.0"):
                        sum=sum+len(dict[key])
            return sum
        for id in evals.keys():
            value=int(evals[id])
            if value >-1:
                id_area=calculate_area(float(dis_dict[id]))
                if id_area in sys_area_dict.keys():
                    co = sys_area_dict.get(id_area)
                    co.append(id)
                    sys_area_dict.update({id_area: co})
                else:
                    sys_area_dict[id_area] = [id]
        areas=['0','0.4','0.5','0.55','0.6','0.65','0.7','0.75','0.8','0.85','0.9','0.95','1','1.0']
        print(key)
        for ar in areas:
            sys_sum=get_area_sum(sys_area_dict,ar)
            total_sum=get_area_sum(area_dict,ar)
            print(ar,":",sys_sum,total_sum)
            #print(ar,str(round(sys_sum*100/total_sum,2))+'%')
        print('='*50)
analyze_distance()

