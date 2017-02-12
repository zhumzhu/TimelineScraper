import json,logging
import pika

class RabbitmqResultsStore(object):
    
    @staticmethod
    def get_config_params():
        return [{"name":"queue_name", "type":"String"}]

    def __init__(self, name, workspace, queue_name):    
        self.logger = logging.getLogger(name)
        self.queue_name = queue_name

        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost', heartbeat_interval=0)
             )

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name)

    def __del__(self):
        self.connection.close()
        
    def store_dict_as_json(self,result_dict):
        json_encoded_status = json.dumps(result_dict, sort_keys=True)
        self.store_string(json_encoded_status)

    # Stores string as a newline in the output file
    def store_string(self,string_to_store):
        self.channel.basic_publish(
            exchange='', 
            routing_key=self.queue_name, 
            body=string_to_store,
            properties = pika.BasicProperties(content_type='application/json'))
        
    # Kept for legacy, deprecated. Use store_dict_as_json or store_string
    def store(self,result):
        self.logger.error("FileSystemResultsStore.store is deprecated")
        pass


