import numpy as np

from Recoder.run2 import train

train(256, "/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/trn_data.pkl",
      "/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/rulead.pkl",
      valdatapkl_f="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/val_data.pkl",
      save_dir="/home/zhongwenkang3/BigTrnSave/Recoder",
      nl_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/nl_voc.pkl",
      rule_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/rule.pkl",
      code_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/code_voc.pkl",
      char_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/char_voc.pkl",
      max_epoch=20, task_name="Recoder")