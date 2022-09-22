from Recoder.Dataset import SumDataset
class dotdict(dict):
    def __getattr__(self, name):
        return self[name]
args = dotdict({
    'NlLen':500,
    'CodeLen':60,
    'batch_size':40,
    'embedding_size':256,
    'WoLen':15,
    'Vocsize':100,
    'Nl_Vocsize':100,
    'max_step':3,
    'margin':0.5,
    'poolsize':50,
    'Code_Vocsize':100,
    'num_steps':50,
    'rulenum':10,
    'cnum':695
})
dset = SumDataset(args,dataName="val",process_data_f="",
                  nl_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/trn_nl.pkl",
                  trndatapkl_f="",valdatapkl_f="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/val_data.pkl",
                  val_nl_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/val_nl.pkl",
                  val_process_data_f="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/process_data_val.pkl",
                  nl_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/nl_voc.pkl",
                  rule_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/rule.pkl",
                  code_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/code_voc.pkl",
                  char_voc_path="/home/zhongwenkang3/NPR4J_Data/BigTrain_Processed/Recoder/char_voc.pkl")