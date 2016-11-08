import boto3,os
from timelinescraper.resultstore.FileSystemResultsStore import FileSystemResultsStore

class S3ResultsStore(FileSystemResultsStore):
    
    @staticmethod
    def get_config_params():
        return [{"name":"bucket_name", "type":"String"},
                {"name":"rollover trigger size in bytes", "type":"Integer"}]

    def __init__(self, name, workspace, bucket_name, rollover_trigger_size = 1e6):
        super(S3ResultsStore,self).__init__(name, workspace, 
            rollover_enabled = True, 
            rollover_trigger_size = rollover_trigger_size)
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3')

        self.s3_filename = self.filename.replace(workspace+"/","")
        
        # Identifying max rollover number
        self.max_rollover_number = 0
        for s3_object in self.s3.Bucket(self.bucket_name).objects.all():
            # self.logger.debug("S3ResultsStore found resource with key: %s" % (s3_object.key) )
            object_key_splitted = s3_object.key.split('.')

            object_filename = '.'.join(object_key_splitted[:-1])

            if object_filename==self.s3_filename and object_key_splitted[-1].isdigit() \
             and int(object_key_splitted[-1])>self.max_rollover_number:
                self.max_rollover_number = int(object_key_splitted[-1])
                # self.logger.debug("S3ResultsStore found a new max_rollover_number: %i" % self.max_rollover_number)

        self.logger.debug("S3ResultsStore set new max_rollover_number to: %i" % self.max_rollover_number)


    def do_rollover(self):
    	self.do_rollover_on_s3()

    def do_rollover_on_s3(self):
        self.logger.debug("S3ResultsStore.do_rollover_on_s3 is now performing rollover")
        self.output_file.close()

        # Inspired to RotatingFileHandler.doRollover
        # http://svn.python.org/projects/python/trunk/Lib/logging/handlers.py
        self.max_rollover_number += 1
        os.rename(self.filename, self.filename+"."+str(self.max_rollover_number))
        
        self.s3.Bucket(self.bucket_name).put_object(
            Key=self.s3_filename+"."+str(self.max_rollover_number), 
            Body=open(self.filename+"."+str(self.max_rollover_number), 'rb'))

        # delete the old file
        os.remove(self.filename+"."+str(self.max_rollover_number))
        
        # reopen the output file
        self.output_file = open(self.filename,'a',1)

