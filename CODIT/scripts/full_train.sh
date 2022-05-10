for data_name in code_chnage_data; do
  for kind in rule augmented.token token abstract.code ; do
    echo "Training on ${data_name}-${kind}"
    python train.py \
          -data data/processed/${data_name}/$kind \
          -save_model models/${data_name}/$kind \
          --type token \
          -valid_steps 500 \
          -gpuid 0 \
          -batch_size 16 \
          --type token \
          -report_every 500 \
          -train_steps 50000;
  done
done
