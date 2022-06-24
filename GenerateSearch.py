import random

import yaml
from random import sample


def search_CoCoNut(examples_num):
    for i in range(1,examples_num+1):
        dropout=abs(random.random()-0.5)
        learning_rate=abs(random.random()-0.5)
        share_input_output_embed="true" if random.random()>0.5 else 'false'
        encoder_embed_dim=sample(range(128,512,32),1)[0]
        decoder_embed_dim = encoder_embed_dim
        decoder_out_embed_dim = encoder_embed_dim if share_input_output_embed=="true" else sample(range(128,512,32),1)[0]
        encoder_layers='[('+str(sample(range(128,640,128),1)[0])+','+str(random.randint(1,10))+')] * '+str(random.randint(1,10))
        decoder_layers = '[(' + str(sample(range(128, 640, 128), 1)[0]) + ',' + str(random.randint(1, 10)) + ')] * ' + str(random.randint(1, 10))
        momentum = random.random()
        clip_norm=random.random()
        optimizer=sample(["sgd","adagrad","nag"],1)[0]
        criterion=sample(["label_smoothed_cross_entropy","cross_entropy"],1)[0]

        #
        configdict = {}
        configdict["dropout"] = dropout
        configdict["share_input_output_embed"] = share_input_output_embed
        configdict["encoder_embed_dim"] = encoder_embed_dim
        configdict["decoder_embed_dim"] = decoder_embed_dim
        configdict["decoder_out_embed_dim"] = decoder_out_embed_dim
        configdict["encoder_layers"] = encoder_layers
        configdict["decoder_layers"] = decoder_layers
        configdict["lr"] = learning_rate
        configdict["momentum"] = momentum
        configdict["clip_norm"] = clip_norm
        configdict["optimizer"] = optimizer
        configdict["criterion"] = criterion
        configdict["savedir"] = "/root/zwk/DDPR_DATA/CoCoNut/CoCoNut_" + str(i)+"_save"
        configdict["trainbin"] = '/root/zwk/NPR_DATA0306/Processed_CoCoNut/dest'
        configdict["batch_size"] = 64
        configdict['device_id'] = 0
        configdict['max-epoch'] = 20
        with open("ConfigSearch/CoCoNut/CoCoNut_" + str(i) + "_20872.yaml", 'w', encoding='utf8') as af:
            yaml.dump(configdict, af)
            af.close()

def search_Codit(examples_num):
    for i in range(11,examples_num+11):
        with open("ConfigSearch/Codit/Codit_augtoken_template.yaml", 'r') as f:
            augtoken_config = yaml.safe_load(f)
            f.close()
        with open("ConfigSearch/Codit/Codit_rule_template.yaml", 'r') as rf:
            rule_config = yaml.safe_load(rf)
            rf.close()
        word_vec_size=sample(range(128,640,128),1)[0]
        rnn_size=word_vec_size
        learning_rate=abs(random.random()-0.5)
        max_grad_norm=random.randint(1,5)
        dropout = abs(random.random() - 0.5)
        src_vocab_size=random.randint(20000,100000)
        aug_log_file="/root/zwk/NPR_DATA0306/Processed_Codit/save/augtoken_"+str(i)+"/augtoken_"+str(i)+'.log'
        aug_save_model="/root/zwk/NPR_DATA0306/Processed_Codit/save/augtoken_"+str(i)+"/augtoken_"+str(i)
        aug_tensorboard="/root/zwk/NPR_DATA0306/Processed_Codit/save/augtoken_"+str(i)+"/augtoken_"+str(i)+'.tensorlog'

        rule_log_file = "/root/zwk/NPR_DATA0306/Processed_Codit/save/rule_" + str(i) + "/rule_" + str(i) + '.log'
        rule_save_model = "/root/zwk/NPR_DATA0306/Processed_Codit/save/rule_" + str(i) + "/rule_" + str(i)
        rule_tensorboard = "/root/zwk/NPR_DATA0306/Processed_Codit/save/rule_" + str(i) + "/rule_" + str(
            i) + '.tensorlog'

        augtoken_config["word_vec_size"]=word_vec_size
        augtoken_config["rnn_size"]=rnn_size
        augtoken_config["learning_rate"]=learning_rate
        augtoken_config["max_grad_norm"]=max_grad_norm
        augtoken_config["dropout"]=dropout
        augtoken_config["log_file"]=aug_log_file
        augtoken_config["save_model"] = aug_save_model
        augtoken_config["tensorboard_log_dir"] = aug_tensorboard
        augtoken_config["src_vocab_size"]=src_vocab_size
        augtoken_config["tgt_vocab_size"] = src_vocab_size

        rule_config["word_vec_size"]=word_vec_size
        rule_config["rnn_size"]=rnn_size
        rule_config["learning_rate"]=learning_rate
        rule_config["max_grad_norm"]=max_grad_norm
        rule_config["dropout"]=dropout
        rule_config["log_file"]=rule_log_file
        rule_config["save_model"] = rule_save_model
        rule_config["tensorboard_log_dir"] = rule_tensorboard
        rule_config["src_vocab_size"]=src_vocab_size
        rule_config["tgt_vocab_size"] = src_vocab_size

        with open("ConfigSearch/Codit/Codit_augtoken" + str(i) + "_20872.yaml", 'w', encoding='utf8') as af:
            yaml.dump(augtoken_config, af)
            af.close()
        with open("ConfigSearch/Codit/Codit_rule" + str(i) + "_20872.yaml", 'w', encoding='utf8') as af:
            yaml.dump(rule_config, af)
            af.close()
        pass

def search_SequenceR(examples_num):
    for i in range(21,examples_num+21):
        with open("ConfigSearch/SequenceR/SequenceR_template.yaml", 'r') as f:
            SR_config = yaml.safe_load(f)
            f.close()

        word_vec_size = sample(range(128, 640, 128), 1)[0]
        rnn_size = word_vec_size
        learning_rate = abs(random.random() - 0.5)
        max_grad_norm = random.randint(1, 5)
        dropout = abs(random.random() - 0.5)
        src_vocab_size = random.randint(40000, 200000)
        tgt_vocab_size = random.randint(20000, 100000)

        log_file="/root/zwk/NPR_DATA0306/Processed_SR/save/SR_"+str(i)+"/SR_"+str(i)+'.log'
        save_model="/root/zwk/NPR_DATA0306/Processed_SR/save/SR_"+str(i)+"/SR_"+str(i)
        tensorboard="/root/zwk/NPR_DATA0306/Processed_SR/save/SR_"+str(i)+"/SR_"+str(i)+'.tensorlog'

        SR_config["word_vec_size"] = word_vec_size
        SR_config["rnn_size"] = rnn_size
        SR_config["learning_rate"] = learning_rate
        SR_config["max_grad_norm"] = max_grad_norm
        SR_config["dropout"] = dropout
        SR_config["log_file"] = log_file
        SR_config["save_model"] = save_model
        SR_config["tensorboard_log_dir"] = tensorboard
        SR_config["src_vocab_size"] = src_vocab_size
        SR_config["tgt_vocab_size"] = tgt_vocab_size

        with open("ConfigSearch/SequenceR/SR_"+str(i)+"_20872.yaml",'w',encoding='utf8') as f:
            yaml.dump(SR_config, f)
            f.close()
def search_Tufano(examples_num):
    for i in range(1,examples_num+1):
        with open("ConfigSearch/Tufano/Tufano_template.yaml", 'r') as f:
            SR_config = yaml.safe_load(f)
            f.close()

        word_vec_size = sample(range(128, 640, 128), 1)[0]
        rnn_size = word_vec_size
        learning_rate = abs(random.random() - 0.5)
        max_grad_norm = random.randint(1, 5)
        dropout = abs(random.random() - 0.5)


        log_file="/root/zwk/NPR_DATA0306/Processed_Tufano/save/Tufano_"+str(i)+"/Tufano_"+str(i)+'.log'
        save_model="/root/zwk/NPR_DATA0306/Processed_Tufano/save/Tufano_"+str(i)+"/Tufano_"+str(i)
        tensorboard="/root/zwk/NPR_DATA0306/Processed_Tufano/save/Tufano_"+str(i)+"/Tufano_"+str(i)+'.tensorlog'

        SR_config["word_vec_size"] = word_vec_size
        SR_config["rnn_size"] = rnn_size
        SR_config["learning_rate"] = learning_rate
        SR_config["max_grad_norm"] = max_grad_norm
        SR_config["dropout"] = dropout
        SR_config["log_file"] = log_file
        SR_config["save_model"] = save_model
        SR_config["tensorboard_log_dir"] = tensorboard


        with open("ConfigSearch/Tufano/Tufano_"+str(i)+"_20872.yaml",'w',encoding='utf8') as f:
            yaml.dump(SR_config, f)
            f.close()

def search_Recoder(examples_num):
    for i in range(1,examples_num+1):
        with open("ConfigSearch/Recoder/Recoder_template.yaml", 'r') as f:
            Recoder_config = yaml.safe_load(f)
            f.close()

        embedding_size = sample(range(128, 640, 128), 1)[0]
        with open("ConfigSearch/Recoder/Recoder_"+str(i)+"_20872.yaml",'w',encoding='utf8') as f:
            yaml.dump(Recoder_config, f)
            f.close()





