import json,time
import threading

class FileSystemResultsStore(object):
	def __init__(self,timeline_scraper):
		#self.threadLock = threading.Lock()
		query = timeline_scraper.name.replace("/","-")
		self.filename=timeline_scraper.workspace+"/"+query+".data.txt"
		self.output_file = open(self.filename,'a',1)
		
	def store_dict_as_json(self,result_dict):
		json_encoded_status = json.dumps(result, sort_keys=True)

		self.store_string(json_encoded_status)

	# Stores string as a newline in the output file
	def store_string(self,string_to_store):
		self.output_file.write(string_to_store+'\n')

	# Kept for legacy, deprecated. Use store_dict_as_json or store_string
	def store(self,result):
		# Get lock to synchronize threads
		# self.threadLock.acquire()
		json_encoded_status = json.dumps(result, sort_keys=True)
		# print("storing result",json_encoded_status)
		self.output_file.write(json_encoded_status+'\n')
		# Free lock to release next thread
		# self.threadLock.release()

	def __del__(self):
		self.output_file.close()
