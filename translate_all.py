import os
import time
import torch
def translate_all_CoCoNut(dir):

    configs=os.listdir(dir)
    for config in configs:
        if str(config.endswith(".yaml")):
            cmd = "python translate.py -model CoCoNut -config "+dir+"/"+config
            print(cmd)
            os.system(cmd)
            time.sleep(1)
            torch.cuda.empty_cache()
            time.sleep(1)
translate_all_CoCoNut("/home/zhongwenkang2/NPR4J/Config/translate/CoCoNut")