import os
import pickle


def check_recoder_args(input_dir):

    def Load_Voc(nl_voc_path,code_voc_path,char_voc_path):
        Nl_Voc = {"pad": 0, "Unknown": 1}
        Code_Voc = {"pad": 0, "Unknown": 1}
        Char_Voc = {"pad": 0, "Unknown": 1}
        if os.path.exists(nl_voc_path):
            Nl_Voc = pickle.load(open(nl_voc_path, "rb"))
        if os.path.exists(code_voc_path):
            Code_Voc = pickle.load(open(code_voc_path, "rb"))
        if os.path.exists(char_voc_path):
            Char_Voc = pickle.load(open(char_voc_path, "rb"))
        Nl_Voc["<emptynode>"] = len(Nl_Voc)
        Code_Voc["<emptynode>"] = len(Code_Voc)
        return Nl_Voc,Code_Voc,Char_Voc
    nl_voc,code_voc,char_voc=Load_Voc(input_dir+'/nl_voc.pkl',input_dir+'/code_voc.pkl',input_dir+'/char_voc.pkl')
    print("nl_voc",len(nl_voc))
    print("code_voc",len(code_voc))
    print("char_voc",len(char_voc))
check_recoder_args("E:/NPR4J/TrainedModels/Recoder_original")
