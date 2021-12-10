import os
import argparse
import yaml

from CoCoNut.training.train import train_context


def train_ONMT(config_file,clearML):
    cmd="python OpenNMT-py-master/train.py "+"-config "+config_file +" -clearML "+str(clearML)
    os.system(cmd)

def train_CoCoNut(config_file):
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
    logfile=config_dict['log_file']
    tensor_log=config_dict['tensorboard_logdir']
    train_context(dropout,share_input_output_embed,encoder_embed_dim,decoder_embed_dim,decoder_out_embed_dim,encoder_layers,decoder_layers,lr,momentum,clip_norm,optimizer,criterion,savedir,trainbin,
                  deviceid,batchsize,logfile,tensor_log)
def main():
    parser = argparse.ArgumentParser(
        description='build_vocab.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=True)
    parser.add_argument("-framework", help="", required=True,choices=["onmt","fairseq","None"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.framework=="onmt":
        train_ONMT(config_file=opt.config,clearML=opt.clearML)
    elif opt.framework=="fairseq":
        train_CoCoNut(config_file=opt.config)

if __name__ == "__main__":
    #train_CoCoNut("D:\DDPR\Config\CoCoNut\\20889_CoCoNut_o9.YAML")
    main()



