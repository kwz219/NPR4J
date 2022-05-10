dataset=code_change_data
bs=$1
input_base_path="/home/saikatc/Research/OpenNMT-py/data/raw/${dataset}/test/";
model_path="/home/saikatc/Research/OpenNMT-py/models/${dataset}/abstract.code-best-acc.pt"

echo $input_base_path
echo $model_path
command='python translate_token_only.py -model '$model_path'
        -src '$input_base_path'prev.abstract.code -tgt '$input_base_path'next.abstract.code
        --name '$dataset'/abstract.code -beam_size '$bs' -n_best '$bs' -replace_unk -verbose -batch_size 64'
#        -verbose
echo $command
$command
