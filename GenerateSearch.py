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


search_CoCoNut(100)

