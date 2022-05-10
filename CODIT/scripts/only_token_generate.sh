dataset=code_change_data
bs=$1
input_base_path="/home/saikatc/Research/OpenNMT-py/data/raw/${dataset}/test/";
model_path="/home/saikatc/Research/OpenNMT-py/models/${dataset}/token-best-acc.pt"
echo $input_base_path
echo $model_path
command='python translate_token_only.py -model '$model_path'
        -src '$input_base_path'prev.token -tgt '$input_base_path'next.token
        --name '$dataset'/token-only -beam_size '$bs' -n_best '$bs' -replace_unk -verbose -batch_size 16'
#        -verbose
echo $command
$command
