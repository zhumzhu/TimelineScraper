import json,time,logging
import os
import threading

class FileSystemResultsStore(object):
    
    @staticmethod
    def get_config_params():
        return [{"name":"rollover_enabled", "type":"String"},
                {"name":"rollover_trigger_size", "type":"String"}]

    def __init__(self, name, workspace, rollover_enabled = True, rollover_trigger_size = 1e6):
        #self.threadLock = threading.Lock()
        query = name.replace("/","-")
        query = name.replace(".","")
        self.filename=workspace+"/"+query+".data.txt"
        self.output_file = open(self.filename,'a',1)
        
        # setup logging
        self.logger = logging.getLogger(name)
        
        self.rollover_enabled = rollover_enabled
        self.rollover_trigger_size = rollover_trigger_size
        
    def store_dict_as_json(self,result_dict):
        json_encoded_status = json.dumps(result_dict, sort_keys=True)
        self.store_string(json_encoded_status)

    # Stores string as a newline in the output file
    def store_string(self,string_to_store):
        self.output_file.write(string_to_store+'\n')

        # check if the file size is bigger than a threshold
        if self.rollover_enabled and os.stat(self.filename).st_size > self.rollover_trigger_size:
            self.do_rollover()

    def do_rollover(self):
        self.logger.debug("FileSystemResultsStore.store_string file size is bigger than the threshold, going to rollover")
        self.output_file.close()

        # Inspired to RotatingFileHandler.doRollover
        # http://svn.python.org/projects/python/trunk/Lib/logging/handlers.py
        file_number = 0
        while os.path.exists(self.filename+"."+str(file_number)):
            file_number+=1
        os.rename(self.filename, self.filename+"."+str(file_number))

        # reopen the output file
        self.output_file = open(self.filename,'a',1)

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

    def __del__(self):
        self.output_file.close()
