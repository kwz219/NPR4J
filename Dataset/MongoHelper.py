import pymongo
from DataConstants import MONGO_URL,DATABASE
class MongoHelper(object):
    def __init__(self):
        self.mongoClient=pymongo.MongoClient(MONGO_URL)
        self.db=self.mongoClient[DATABASE]
    def get_col(self,COL_NAME):
        return self.db[COL_NAME]
