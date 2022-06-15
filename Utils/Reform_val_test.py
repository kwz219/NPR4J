from Utils.CA_Utils import writeL2F
from Utils.IOHelper import readF2L
import random
import os
import shutil
def reform_val_test(val_ids_f,test_ids_f,val_dir,test_dir,test_oids,new_val_dir,new_test_dir):
    test_oids=readF2L(test_oids)
    test_ids=readF2L(test_ids_f)
    val_ids=readF2L(val_ids_f)
    choice_ids_num=len(test_ids)-len(test_oids)
    test_add_ids=random.sample(val_ids,choice_ids_num)
    val_remain_ids=list(set(val_ids)-set(test_add_ids))
    val_add_ids=list(set(test_ids)-set(test_oids))
    def make_dirs(root_dir):
        os.makedirs(root_dir)
        os.makedirs(root_dir + '/buggy_lines')
        os.makedirs(root_dir + '/buggy_methods')
        os.makedirs(root_dir + '/buggy_classes')
        os.makedirs(root_dir + '/fix_lines')
        os.makedirs(root_dir + '/fix_methods')
        os.makedirs(root_dir + '/fix_classes')
        os.makedirs(root_dir+'/metas')
    #test_oids,test_addids
    print(test_dir,val_dir)

    #make_dirs(new_test_dir)
    for id in test_oids:
        print(os.path.join(test_dir,"buggy_lines/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"buggy_lines/"+id+'.txt'),os.path.join(new_test_dir,"buggy_lines/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"buggy_methods/"+id+'.txt'),os.path.join(new_test_dir,"buggy_methods/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"buggy_classes/"+id+'.txt'),os.path.join(new_test_dir,"buggy_classes/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_lines/"+id+'.txt'),os.path.join(new_test_dir,"fix_lines/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_methods/"+id+'.txt'),os.path.join(new_test_dir,"fix_methods/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_classes/"+id+'.txt'),os.path.join(new_test_dir,"fix_classes/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"metas/"+id+'.txt'),os.path.join(new_test_dir,"metas/"+id+'.txt'))
    for id in test_add_ids:
        shutil.copy(os.path.join(val_dir,"buggy_lines/"+id+'.txt'),os.path.join(new_test_dir,"buggy_lines/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"buggy_methods/"+id+'.txt'),os.path.join(new_test_dir,"buggy_methods/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"buggy_classes/"+id+'.txt'),os.path.join(new_test_dir,"buggy_classes/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_lines/"+id+'.txt'),os.path.join(new_test_dir,"fix_lines/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_methods/"+id+'.txt'),os.path.join(new_test_dir,"fix_methods/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_classes/"+id+'.txt'),os.path.join(new_test_dir,"fix_classes/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"metas/"+id+'.txt'),os.path.join(new_test_dir,"metas/"+id+'.txt'))


    #val_remain_ids,val_add_ids
    make_dirs(new_val_dir)
    for id in val_remain_ids:
        shutil.copy(os.path.join(val_dir,"buggy_lines/"+id+'.txt'),os.path.join(new_val_dir,"buggy_lines/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"buggy_methods/"+id+'.txt'),os.path.join(new_val_dir,"buggy_methods/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"buggy_classes/"+id+'.txt'),os.path.join(new_val_dir,"buggy_classes/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_lines/"+id+'.txt'),os.path.join(new_val_dir,"fix_lines/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_methods/"+id+'.txt'),os.path.join(new_val_dir,"fix_methods/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"fix_classes/"+id+'.txt'),os.path.join(new_val_dir,"fix_classes/"+id+'.txt'))
        shutil.copy(os.path.join(val_dir,"metas/"+id+'.txt'),os.path.join(new_val_dir,"metas/"+id+'.txt'))
    for id in val_add_ids:
        shutil.copy(os.path.join(test_dir,"buggy_lines/"+id+'.txt'),os.path.join(new_val_dir,"buggy_lines/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"buggy_methods/"+id+'.txt'),os.path.join(new_val_dir,"buggy_methods/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"buggy_classes/"+id+'.txt'),os.path.join(new_val_dir,"buggy_classes/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_lines/"+id+'.txt'),os.path.join(new_val_dir,"fix_lines/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_methods/"+id+'.txt'),os.path.join(new_val_dir,"fix_methods/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"fix_classes/"+id+'.txt'),os.path.join(new_val_dir,"fix_classes/"+id+'.txt'))
        shutil.copy(os.path.join(test_dir,"metas/"+id+'.txt'),os.path.join(new_val_dir,"metas/"+id+'.txt'))

    writeL2F(val_remain_ids+val_add_ids,new_val_dir+'/valid.ids')
    writeL2F(test_oids + test_add_ids, new_test_dir + '/test.ids')

#reform_val_test("/home/zhongwenkang/RawData/Valid/valid.ids","/home/zhongwenkang/RawData/Diversity_Main/success.ids",
                #"/home/zhongwenkang/RawData/Valid","/home/zhongwenkang/RawData/Diversity_Main",
                #"/home/zhongwenkang/RawData/Diversity_Main/oneline.ids","/home/zhongwenkang/RawData/new_val","/home/zhongwenkang/RawData/new_test")
