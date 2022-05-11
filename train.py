import os
import argparse
import subprocess

import yaml

from CoCoNut.training.train import train_context, train_fconv, train_trans


def train_ONMT(config_file,clearML):
    with open(config_file,'r') as f:
        config_dict=yaml.safe_load(f)
    # filter long examples
    src_seq_length=config_dict["src_seq_length"]
    tgt_seq_length=config_dict["tgt_seq_length"]
    src_seq_length_trunc=config_dict["src_seq_length_trunc"]
    tgt_seq_length_trunc=config_dict["tgt_seq_length_trunc"]

    # vocabulary
    share_vocab=config_dict["share_vocab"]
    dynamic_dict=config_dict["dynamic_dict"]
    src_vocab_size=config_dict["src_vocab_size"]
    tgt_vocab_size=config_dict["tgt_vocab_size"]
    src_vocab=config_dict["src_vocab"]
    tgt_vocab=config_dict["tgt_vocab"]

    # model parameters
    if "copy_attn" in config_dict.keys():
        copy_attn=config_dict["copy_attn"]
    if "copy_loss_by_seqlength" in config_dict.keys():
        copy_loss_by_seqlength=config_dict["copy_loss_by_seqlength"]
    if "reuse_copy_attn" in config_dict.keys():
        reuse_copy_attn=config_dict["reuse_copy_attn"]
    global_attention=config_dict["global_attention"]
    word_vec_size=config_dict["word_vec_size"]
    rnn_size=config_dict["rnn_size"]
    bridge=config_dict["bridge"]
    layers=config_dict["layers"]
    encoder_type=config_dict["encoder_type"]
    early_stopping=config_dict["early_stopping"]
    early_stopping_criteria=config_dict["early_stopping_criteria"]
    train_steps=config_dict["train_steps"]
    valid_steps=config_dict["valid_steps"]
    save_checkpoint_steps=config_dict["save_checkpoint_steps"]
    max_grad_norm=config_dict["max_grad_norm"]
    dropout=config_dict["dropout"]
    batch_size=config_dict["batch_size"]
    valid_batch_size=config_dict["valid_batch_size"]
    optim=config_dict["optim"]
    learning_rate=config_dict["learning_rate"]
    adagrad_accumulator_init=config_dict["adagrad_accumulator_init"]

    cmd="python OpenNMT-py-master/train.py "+"-config "+config_file +" -clearML "+str(clearML)

    #cmd = "python OpenNMT-py-master/train.py " + "-config " + config_file + " -clearML " + str(clearML)
    os.system(cmd)
def train_FConv(config_file,clearml=False):
    with open(config_file,'r') as f:
        config_dict=yaml.safe_load(f)

    print(config_dict)
    dropout=config_dict['dropout']
    share_input_output_embed=config_dict['share_input_output_embed']
    encoder_embed_dim=config_dict['encoder_embed_dim']
    decoder_embed_dim=config_dict['decoder_embed_dim']
    decoder_out_embed_dim=config_dict['decoder_out_embed_dim']
    encoder_layers=config_dict['encoder_layers']
    decoder_layers=config_dict['decoder_layers']
    lr=config_dict['lr']
    momentum=config_dict['momentum']
    clip_norm=config_dict['clip_norm']
    optimizer=config_dict['optimizer']
    criterion=config_dict['criterion']
    savedir=config_dict['savedir']
    trainbin=config_dict['trainbin']
    deviceid=config_dict['device_id']
    batchsize=config_dict['batch_size']
    max_epoch=config_dict['max-epoch']
    use_clearml=clearml
    experiment_id=config_file.split('/')[-1].replace(".yaml",'')
    train_fconv(dropout,share_input_output_embed,encoder_embed_dim,decoder_embed_dim,decoder_out_embed_dim,encoder_layers,decoder_layers,lr,momentum,clip_norm,optimizer,criterion,savedir,trainbin,
                  deviceid,batchsize,max_epoch,use_clearml,experiment_id)
def train_CoCoNut(config_file,clearml=False):
    with open(config_file,'r') as f:
        config_dict=yaml.safe_load(f)
    print(config_dict)
    dropout=config_dict['dropout']
    share_input_output_embed=config_dict['share_input_output_embed']
    encoder_embed_dim=config_dict['encoder_embed_dim']
    decoder_embed_dim=config_dict['decoder_embed_dim']
    decoder_out_embed_dim=config_dict['decoder_out_embed_dim']
    encoder_layers=config_dict['encoder_layers']
    decoder_layers=config_dict['decoder_layers']
    lr=config_dict['lr']
    momentum=config_dict['momentum']
    clip_norm=config_dict['clip_norm']
    optimizer=config_dict['optimizer']
    criterion=config_dict['criterion']
    savedir=config_dict['savedir']
    trainbin=config_dict['trainbin']
    deviceid=config_dict['device_id']
    batchsize=config_dict['batch_size']
    max_epoch=config_dict['max-epoch']
    use_clearml=clearml
    experiment_id=config_file.split('/')[-1].replace(".yaml",'')
    train_context(dropout,share_input_output_embed,encoder_embed_dim,decoder_embed_dim,decoder_out_embed_dim,encoder_layers,decoder_layers,lr,momentum,clip_norm,optimizer,criterion,savedir,trainbin,
                  deviceid,batchsize,max_epoch,use_clearml,experiment_id)
def train_Cure(config_file,clearml=False):
    with open(config_file,'r') as f:
        config_dict=yaml.safe_load(f)
    dropout=config_dict['dropout']
    share_input_output_embed=config_dict['share_input_output_embed']
    encoder_embed_dim=config_dict['encoder_embed_dim']
    decoder_embed_dim=config_dict['decoder_embed_dim']
    decoder_out_embed_dim=config_dict['decoder_out_embed_dim']
    encoder_layers=config_dict['encoder_layers']
    decoder_layers=config_dict['decoder_layers']
    lr=config_dict['lr']
    momentum=config_dict['momentum']
    clip_norm=config_dict['clip_norm']
    optimizer=config_dict['optimizer']
    criterion=config_dict['criterion']
    savedir=config_dict['savedir']
    trainbin=config_dict['trainbin']
    deviceid=config_dict['device_id']
    batchsize=config_dict['batch_size']
    max_epoch=config_dict['max-epoch']
    experiment_id = config_file.split('/')[-1].replace(".yaml", '')

    if not os.path.exists(savedir):
        os.makedirs(savedir)

    if share_input_output_embed:
        share = ' --share-input-output-embed '
    else:
        share = ''

    cmd = 'python fairseq/train.py --task cure --skip-invalid-size-inputs-valid-test --save-dir ' + savedir + \
          ' --arch cure  --max-tokens 2000 --distributed-world-size 1  --log-format json ' + \
          '--encoder-embed-dim ' + str(encoder_embed_dim) + \
          ' --decoder-embed-dim ' + str(decoder_embed_dim) + \
          ' --decoder-out-embed-dim ' + str(decoder_out_embed_dim) + \
          ' --encoder-layers "' + encoder_layers + \
          '" --decoder-layers "' + decoder_layers + \
          '" --dropout ' + str(dropout) + \
          share + \
          ' --clip-norm ' + str(clip_norm) + \
          ' --lr ' + str(lr) + \
          ' --optimizer ' + optimizer + \
          ' --criterion ' + criterion + \
          ' --momentum ' + str(momentum) + \
          ' --max-epoch ' + str(max_epoch) + \
          ' --no-epoch-checkpoints  --min-lr 1e-4   --batch-size 48 ' + trainbin + \
          ' --batch-size ' + str(batchsize) + \
          ' --device-id ' + str(deviceid) + \
          ' -clearml ' + str(clearml) + \
          ' -experiment_name ' + experiment_id


    #cmd = cmd + " | tee " + savedir + "/log.txt"
    print(cmd)
    subprocess.call(cmd, shell=True)
def train_Recoder(config_file):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
    trn_data=config_dict["trn_data_pkl"]
    val_data=config_dict["valdata_pkl"]
    save_dir=config_dict["save_dir"]
    nl_voc=config_dict["nl_voc_path"]
    rule=config_dict["rule_path"]
    code_voc=config_dict["code_voc_path"]
    char_voc=config_dict["char_voc_path"]
    max_epoch=config_dict["max_epoch"]

    cmd="python ./Recoder/run.py -trn_data "+trn_data +" -val_data "+val_data+" -save_dir "+save_dir+" -nl_voc "+nl_voc\
        +" rule "+rule+" code_voc "+code_voc+" char_voc "+char_voc+" max_epoch "+str(max_epoch)
    os.system(cmd)
def train_Edits(config_file):
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
    pass
def main():
    parser = argparse.ArgumentParser(
        description='build_vocab.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=False)
    parser.add_argument("-model", help="", required=True,choices=["onmt","fairseq","Cure","CoCoNut","FConv","CODIT","Recoder","Edits"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.model=="onmt":
        train_ONMT(config_file=opt.config,clearML=opt.clearml)
    elif opt.model=="CoCoNut":
        train_CoCoNut(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="Cure":
        train_Cure(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="FConv":
        train_FConv(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="Recoder":
        train_Recoder(opt.config)
    elif opt.model=="Edits":
        train_Edits(opt.config)




if __name__ == "__main__":
    #train_CoCoNut("D:\DDPR\Config\CoCoNut\\CoCoNut_test.yaml")
    #train_FConv("D:\DDPR\Config\CoCoNut\Ali_FconvLine_o1.yaml",True)
    main()
    #train_Cure("D:\DDPR\Config\Cure\cure_test.yaml",False)
    #train_CoCoNut("D:\DDPR\Config\CoCoNut\CoCoNut_test.yaml",False)



