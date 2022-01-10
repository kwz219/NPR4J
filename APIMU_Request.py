import requests


def test_request():
    url = 'http://172.29.7.223:5069/repair'
    #apiseq: 提取出的api序列,每个api之间以空格隔开
    #num_hypotheses: 生成多少个修复方案
    #beam_size: 设置和num_hypotheses一样就行了
    test_json={"apiseq":"java.util.List.size() java.util.ArrayList.init(int) <for_condition> java.util.List.size() </for_condition> <for_body> java.lang.String.valueOf(int) java.lang.System.currentTimeMillis() java.lang.Class.getSimpleName() </for_body>",
               "beam_size":5,
               "num_hypotheses":5}
    result=requests.post(url=url,json=test_json)
    #result: json格式，每一条是一个修复方案
    print("results",result.text)

test_request()