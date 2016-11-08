import json,logging
import pika

class RabbitmqResultsStore(object):
    
    @staticmethod
    def get_config_params():
        return [{"name":"rabbitmq_exchange_name", "type":"String"}]

    def __init__(self, name, workspace, rabbitmq_exchange_name):    
        self.logger = logging.getLogger(name)
        self.rabbitmq_exchange_name = rabbitmq_exchange_name


        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost', heartbeat_interval=0)
             )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.rabbitmq_exchange_name, type='fanout')

    def __del__(self):
        self.connection.close()
        
    def store_dict_as_json(self,result_dict):
        json_encoded_status = json.dumps(result_dict, sort_keys=True)
        self.store_string(json_encoded_status)

    # Stores string as a newline in the output file
    def store_string(self,string_to_store):
        self.channel.basic_publish(
            exchange=self.rabbitmq_exchange_name, 
            routing_key='', 
            body=string_to_store,
            properties = pika.BasicProperties(content_type='application/json'))
        
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


