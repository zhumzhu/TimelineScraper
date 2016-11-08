import json,logging

import zmq

class ZmqResultsStore(object):
    
    @staticmethod
    def get_config_params():
        return []

    def __init__(self, name, workspace):        
        # setup logging
        self.logger = logging.getLogger(name)
        self.topic = name

        port = "5556"
        host = "127.0.0.1"

        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://%s:%s" % (host,port))
    
    def __del__(self):
        pass 
        
    def store_dict_as_json(self,result_dict):
        self.socket.send_json(result_dict)

    # Stores string as a newline in the output file
    def store_string(self,string_to_store):
        raise NotImplementedError("store_string is not used in ZmqResultStore")

    # Kept for legacy, deprecated. Use store_dict_as_json or store_string
    def store(self,result):
        self.logger.warning("FileSystemResultsStore.store is deprecated")
        # Get lock to synchronize threads
        # self.threadLock.acquire()
        json_encoded_status = json.dumps(result, sort_keys=True)
        # print("storing result",json_encoded_status)
        self.output_file.write(json_encoded_status+'\n')
        # Free lock to release next thread
        # self.threadLock.release()


