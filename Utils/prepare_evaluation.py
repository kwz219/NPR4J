import codecs
import pandas
from Utils.IOHelper import readF2L

def readF2L_nostrip(filepath):
    lines=[]
    with open(filepath,'r',encoding='utf-8')as f:
        for line in f:
            lines.append(line)
        f.close()
    return lines
def prepare_quixbugs(ids_f,input_dir):
    ids=readF2L(ids_f)
    bug_names=[]
    bug_ids=[]
    buggy_methods=[]
    buggy_lines=[]
    develop_patch_lines=[]
    for id in ids:
        meta_infos=codecs.open(input_dir+'/metas/'+id+'.txt','r',encoding='utf8').read().strip().split("<sep>")
        buggy_method=readF2L_nostrip(input_dir+'/buggy_methods/'+id+'.txt')
        buggy_line_id=int(meta_infos[2].split(":")[0][1:])
        buggy_method[buggy_line_id]="<START_BUG> "+buggy_method[buggy_line_id].strip()+" <END_BUG>"+'\n'
        clean_method=[]
        for line in buggy_method:
            if len(line.strip())==0:
                continue
            clean_method.append(line)
        buggy_line=codecs.open(input_dir+'/buggy_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        fix_line=codecs.open(input_dir+'/fix_lines/'+id+'.txt','r',encoding='utf8').read().strip()
        bug_name=meta_infos[-1].split("@")[0].split('\\')[-1].replace(".java",'')

        bug_names.append(bug_name)
        bug_ids.append(id)
        buggy_methods.append(''.join(clean_method))
        buggy_lines.append(buggy_line)
        develop_patch_lines.append(fix_line)
        print(id)

    data_frame=pandas.DataFrame({"Bug-name":bug_names,"Bug-Id":bug_ids,"Buggy-Method":buggy_methods,"Buggy-Line":buggy_lines,
                                 "Develop-Patch-Line":develop_patch_lines})
    data_frame.to_excel("qbs_data.xlsx")
prepare_quixbugs(r"E:\NPR4J\RawData (2)\Benchmarks\qbs.ids.new","E:/NPR4J/RawData (2)/Benchmarks")






