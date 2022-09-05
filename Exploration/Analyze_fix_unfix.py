import codecs
import json


def not_fixed_by_any(content_f,result_f,output_f):
    results=json.load(codecs.open(result_f,'r',encoding='utf8'))
    contents=json.load(codecs.open(content_f,'r',encoding='utf8'))
    for bug in results:
        pass

    pass