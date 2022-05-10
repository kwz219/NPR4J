for data_name in code_change_data; do
  for kind in token rule augmented.token abstract.code; do
    echo ${data_name}' '$kind
    python preprocess.py -train_src data/raw/${data_name}/train/prev.$kind \
                  -train_tgt data/raw/${data_name}/train/next.$kind \
                  -valid_src data/raw/${data_name}/train/prev.$kind \
                  -valid_tgt data/raw/${data_name}/train/next.$kind \
                  -save_data data/processed/${data_name}/$kind \
                  -share_vocab;
  done
done
