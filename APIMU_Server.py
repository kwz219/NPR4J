import json

import ctranslate2
from ctranslate2.translator import TranslationResult
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "api misuse correction"

@app.route('/repair',methods=['POST'])
def repair():
    data = json.loads(request.data.decode())
    beam_size=int(data['beam_size'])
    print("beam_size",beam_size)
    num_hypotheses=int(data['num_hypotheses'])
    api_seq=data['apiseq'].split()
    results=translator.translate_batch([api_seq],beam_size=beam_size,num_hypotheses=num_hypotheses)
    preds=results[0].hypotheses
    jsonresult={}
    for i in range(num_hypotheses):
        jsonresult[str(i+1)]=preds[i]
    return json.dumps(jsonresult)
if __name__ == '__main__':
    translator = ctranslate2.Translator("/home/zhongwenkang/20890onmtdata/ctranslate", device="cpu")

    app.run(host='0.0.0.0',port=5069)