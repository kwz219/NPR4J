from Dataset.Preprocess import preprocess_Tufano
def preprocess_CoCoNut():
    pass
def get_TufanoData(ids_f, input_dir, output_dir, idom_path, raw_dir, name, max_length=1000):
    preprocess_Tufano(ids_f, input_dir, output_dir, idom_path, raw_dir, name)

if __name__ == "__main__":
    ids_f="Dataset/freq50_611/trn_ids.txt"
    idoms_f="CodeAbstract/CA_Resource/idioms.10w"
    input_dir="/root/zwk/DDPR_DATA/Tufano_i10w/trntmp"
    output_dir = "/root/zwk/DDPR_DATA/Tufano_i10w"
    raw_dir="/root/zwk/DDPR_DATA/trn"
    name="trn"
    preprocess_Tufano(ids_f,input_dir,output_dir,idoms_f,"trn")
