default_config={"commits_inrepo":"commits_inrepo.txt","commits_special":"repo&commits_special.txt"}
from DataConstants import METHOD_COL
from MongoHelper import MongoHelper
class DataConfig(object):
    def __init__(self,config=default_config):
        self.config=config
        self.mongoClient=MongoHelper()
    def init_bymode(self):
        pass
    def get_train_ids(self):
        pass



    def get_val_ids(self):
        pass
