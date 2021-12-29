import os
import argparse
import subprocess

import yaml

from CoCoNut.training.train import train_context


def train_ONMT(config_file,clearML):
    cmd="python OpenNMT-py-master/train.py "+"-config "+config_file +" -clearML "+str(clearML)
    os.system(cmd)

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
def main():
    parser = argparse.ArgumentParser(
        description='build_vocab.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-clearml",help="record experiment by clearml",default=True)
    parser.add_argument("-model", help="", required=True,choices=["onmt","fairseq","Cure","CoCoNut"])
    parser.add_argument("-config",help="location of config file",required=True)

    opt=parser.parse_args()
    if opt.model=="onmt":
        train_ONMT(config_file=opt.config,clearML=opt.clearml)
    elif opt.model=="CoCoNut":
        train_CoCoNut(config_file=opt.config,clearml=opt.clearml)
    elif opt.model=="Cure":
        train_Cure(config_file=opt.config,clearml=opt.clearml)

if __name__ == "__main__":
    #train_CoCoNut("D:\DDPR\Config\CoCoNut\\20889_CoCoNut_o9.yaml")
    #main()
    train_Cure("D:\DDPR\Config\Cure\cure_test.yaml",False)
    #train_CoCoNut("D:\DDPR\Config\CoCoNut\CoCoNut_test.yaml",False)



