#!/usr/bin/env bash
dataset=code_change_data # icse, codit
bs=$1
nbest=$bs

input_base_path="/home/saikatc/Research/OpenNMT-py/data/raw/${dataset}/test/";
model_path="/home/saikatc/Research/OpenNMT-py/models/${dataset}/rule-best-acc.pt"
grammar_path="/home/saikatc/Research/OpenNMT-py/data/raw/${dataset}/grammar.bin"


#echo $input_base_path
echo $model_path ' '$bs
python translate_structure.py -model $model_path \
        -src $input_base_path/prev.rule -tgt $input_base_path/next.rule\
        --name ${dataset}/structure-only \
        --grammar $grammar_path -beam_size $bs -n_best $nbest -gpu 0;
