import yaml
def transform_config2yaml(name,configlist):
    configdict={}
    configdict["dropout"]=configlist[0]
    configdict["share_input_output_embed"] = configlist[1]
    configdict["encoder_embed_dim"] = configlist[2]
    configdict["decoder_embed_dim"] = configlist[3]
    configdict["decoder_out_embed_dim"] = configlist[4]
    configdict["encoder_layers"] = configlist[5]
    configdict["decoder_layers"] = configlist[6]
    configdict["lr"] = configlist[7]
    configdict["momentum"] = configlist[8]
    configdict["clip_norm"] = configlist[9]
    configdict["optimizer"] = configlist[10]
    configdict["criterion"] = configlist[11]
    configdict["savedir"] = "/root/zwk/DDPR_DATA/CoCoNut/CoCoNut_"+name
    configdict["trainbin"] = '/root/zwk/NPR_DATA0306/CoCoNut/processed_nocontext_minfreq_2'
    configdict["batch_size"]=32
    configdict['device_id']=0
    configdict['max-epoch']=20
    with open("../../Config/Replicate/trn/CoCoNut_"+name+"_21062.yaml",'w',encoding='utf8') as af:
        yaml.dump(configdict,af)
        af.close()
def transform_all():
    all_configs={
        "context_tune_1":[0.03421960641764166, False, 116, 116, 360, '[(128,4)] * 9', '[(640,10)] * 8', 0.286739379371575,
              0.8469909165285214, 0.7517948821073919, 'nag', 'label_smoothed_cross_entropy'],
        "context_tune_2": [0.021718140440948885, False, 198, 198, 369, '[(384,4)] * 4', '[(512,7)] * 9', 0.7225555286167653,
              0.4437699585817757, 0.34067964000565454, 'nag', 'cross_entropy'],
        "context_tune_3": [0.06179165410667997, True, 107, 107, 107, '[(384,3)] * 2', '[(640,7)] * 7', 0.5923928699341593,
              0.6517291271041699, 0.3515853139423949, 'nag', 'cross_entropy'],
        "context_tune_4": [0.01003413732700531, True, 453, 453, 453, '[(128,7)] * 6', '[(256,5)] * 10', 0.3522433662887732,
              0.8214180717637588, 0.4412316782657021, 'sgd', 'label_smoothed_cross_entropy'],
        "context_tune_5": [0.0059120677320028125, False, 326, 326, 242, '[(512,5)] * 10', '[(640,2)] * 6', 0.9846969173516326,
              0.639484543640567, 0.2927570878644937, 'sgd', 'label_smoothed_cross_entropy'],
        "context_tune_6": [0.03306673139818872, True, 145, 145, 145, '[(384,7)] * 5', '[(256,10)] * 4', 0.02928000941475195,
              0.1619284190760819, 0.8874468307300051, 'adagrad', 'cross_entropy'],
        "context_tune_7": [0.2602310837779551, True, 226, 226, 226, '[(512,7)] * 10', '[(640,8)] * 6', 0.15331494861223294,
              0.8794987236596069, 0.6588269008591344, 'nag', 'label_smoothed_cross_entropy'],
        "context_tune_8": [0.08225774673913022, True, 185, 185, 185, '[(384,8)] * 2', '[(256,9)] * 10', 0.43749747624711577,
              0.41291139635553753, 0.6345506727991334, 'sgd', 'cross_entropy'],
        "context_tune_9": [0.21389838152720164, False, 357, 357, 334, '[(384,4)] * 5', '[(640,5)] * 3', 0.3128703688177207,
              0.8456736601204957, 0.5617417487136113, 'nag', 'label_smoothed_cross_entropy'],
        "context_tune_10": [0.3951528562649428, False, 147, 147, 404, '[(256,8)] * 7', '[(640,10)] * 8', 0.8332647582510894,
              0.4660707330587397, 0.3218981154292455, 'nag', 'cross_entropy'],
    }
    Fconv_configs={
        "nocontext_tune_1":[0.14750324647058333, True, 353, 353, 353, '[(384,6)] * 8', '[(512,10)] * 5', 0.7915283934586732,
            0.5498989114182679, 0.3526243918050602, 'nag', 'cross_entropy'],
        "nocontext_tune_2": [0.0015150814800350965, True, 364, 364, 364, '[(384,3)] * 9', '[(640,4)] * 5', 0.9707029949760514,
            0.8757399970334439, 0.4303474425107823, 'sgd', 'label_smoothed_cross_entropy'],
        "nocontext_tune_3": [0.10016184198732148, False, 318, 318, 424, '[(640,6)] * 5', '[(512,4)] * 7', 0.6139086403831485,
            0.7625187615698749, 0.21037956787358847, 'nag', 'cross_entropy'],
        "nocontext_tune_4": [0.19373178358250154, False, 79, 79, 421, '[(128,7)] * 5', '[(384,7)] * 2', 0.0826909790618301,
            0.9715605504864337, 0.8740403099836496, 'adagrad', 'label_smoothed_cross_entropy'],
        "nocontext_tune_5": [0.013546188834337558, True, 338, 338, 338, '[(512,3)] * 5', '[(256,2)] * 10', 0.4533926744655141,
            0.8739175382786576, 0.453844146437531, 'nag', 'label_smoothed_cross_entropy'],
        "nocontext_tune_6": [0.01746815092960441, True, 205, 205, 205, '[(640,5)] * 10', '[(256,5)] * 3', 0.54895795284263,
            0.5612220821359721, 0.5178729791525679, 'sgd', 'label_smoothed_cross_entropy'],
        "nocontext_tune_7": [0.2725394635166619, False, 177, 177, 133, '[(128,4)] * 9', '[(512,8)] * 9', 0.9918597645185625,
            0.78117645727482, 0.7679435945955843, 'nag', 'cross_entropy'],
        "nocontext_tune_8": [0.11623805689340105, True, 106, 106, 106, '[(128,6)] * 3', '[(128,3)] * 6', 0.3782428365044066,
            0.12996300945594275, 0.7808700149034068, 'adagrad', 'label_smoothed_cross_entropy'],
        "nocontext_tune_9": [0.005533347144345613, True, 165, 165, 165, '[(128,6)] * 8', '[(128,8)] * 7', 0.47614411822815284,
            0.6448042062136476, 0.7076638230384297, 'sgd', 'cross_entropy'],
        "nocontext_tune_10": [0.07968555756083184, False, 298, 298, 150, '[(512,3)] * 7', '[(640,5)] * 4', 0.6761639971947639,
            0.8913040572948645, 0.7197491571968713, 'sgd', 'cross_entropy']

    }
    for key in Fconv_configs.keys():
        transform_config2yaml(key,Fconv_configs[key])
transform_all()

