import torch
from torch import nn
from transformers import T5Tokenizer, T5ForConditionalGeneration, RobertaConfig, RobertaTokenizer, RobertaModel
from transformers.convert_pytorch_checkpoint_to_tf2 import MODEL_CLASSES

from CodeBert_ft.model import Seq2Seq
from Recoder.testone_ghl import load_model_for_test


def count_RewardRepair(model_dir):
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    tokenizer.add_tokens(['{', '}', '<', '^'])

    model = T5ForConditionalGeneration.from_pretrained(model_dir)

    total = sum([param.nelement() for param in model.parameters()])

    print("Number of parameter: ", total)

def count_CodeBERT(load_model_path,model_name_or_path,model_type="roberta",max_target_length=128,beam_size=10):
    MODEL_CLASSES = {'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer)}
    config_class, model_class, tokenizer_class = MODEL_CLASSES[model_type]
    config = config_class.from_pretrained(model_name_or_path)
    tokenizer = tokenizer_class.from_pretrained(model_name_or_path)

    # budild model
    encoder = model_class.from_pretrained(model_name_or_path, config=config)
    decoder_layer = nn.TransformerDecoderLayer(d_model=config.hidden_size, nhead=config.num_attention_heads)
    decoder = nn.TransformerDecoder(decoder_layer, num_layers=6)
    model = Seq2Seq(encoder=encoder, decoder=decoder, config=config,
                    beam_size=beam_size, max_length=max_target_length,
                    sos_id=tokenizer.cls_token_id, eos_id=tokenizer.sep_token_id)
    if load_model_path is not None:
        model.load_state_dict(torch.load(load_model_path))

    total = sum([param.nelement() for param in model.parameters()])

    print("Number of parameter: ", total)

#count_CodeBERT("/home/zhongwenkang/NPR_Data/Models/CodeBERT-ft/save/pytorch_model.bin","/home/zhongwenkang/NPR_Data/Models/CodeBERT-ft/base/codebert-base")

def count_Recoder(model_path,nl_voc_size,code_voc_size,voc_size,rule_num,cnum):
    model=load_model_for_test(model_path,nl_voc_size,code_voc_size,voc_size,rule_num,cnum)
    total = sum([param.nelement() for param in model.parameters()])

    print("Number of parameter: ", total)

count_Recoder("/home/zhongwenkang/NPR_Data/Models/Recoder_original/best_model.ckpt",41696,41696,83,1265,764)