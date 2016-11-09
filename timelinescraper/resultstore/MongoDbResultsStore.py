import json,logging
from pymongo import MongoClient

class MongoDbResultsStore(object):
    
    @staticmethod
    def get_config_params():
        return [
            {"name":"mongodb_database_name", "type":"String"},
            {"name":"mongodb_collection_name", "type":"String"}]

    def __init__(self, name, workspace, mongodb_database_name, mongodb_collection_name):    
        self.logger = logging.getLogger(name)
        self.mongodb_collection_name = mongodb_collection_name

        self.collection = MongoClient()[mongodb_database_name][mongodb_collection_name]

    def __del__(self):
        pass
        
    def store_dict_as_json(self,result_dict):
        self.collection.insert_one(result_dict)
        


