import threading,time,sys,traceback,logging
import json,os
from logging.handlers import RotatingFileHandler


# **************************************************************************************************
# TimelineScraper
# **************************************************************************************************
class TimelineScraper(object):
    
    def __init__(self, name, workspace):
        # Logging utilities
        # https://docs.python.org/2/library/logging.html#logging.LogRecord
        formatter = logging.Formatter("%(asctime)s %(levelname)-2s %(name)-2s %(module)s@%(lineno)d.%(funcName)s %(message)s")
        self.logger = logging.getLogger(name)
        # handler = logging.StreamHandler(sys.stdout)
        handler = RotatingFileHandler(workspace+"/"+name.replace(".","").replace("/","-")+".log",
            mode='a', maxBytes=1e6, backupCount=2)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Thread mamagements variables
        self.__condition_variable = threading.Condition()
        self.timelineScraperThread = threading.Thread(target=self.__threadLoop)

        # Config
        self._workspace = workspace
        self._name = name
        
        # Results store
        self._results_store_list = []

        # Obtain status in order to work with timelines
        self._status = TimelineScraperStatus(self)

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, engine):
        self._engine = engine
    
    @property
    def results_store(self):
        raise TypeError("Unable to get results_store, property no logner available")

    @results_store.setter
    def results_store(self, results_store):
        raise TypeError("Unable to set results_store, property no logner available")
    
    @property
    def workspace(self):
        return self._workspace

    @property
    def name(self):
        return self._name
          
    def add_results_store(self, results_store):
        self._results_store_list.append(results_store)

    def startScraper(self):
        self.__stop_scraping = False
        self.timelineScraperThread = threading.Thread(target=self.__threadLoop)
        self.timelineScraperThread.start()

    def stopScraper(self):
        if self.timelineScraperThread.is_alive():
            self.__condition_variable.acquire()
            self.__stop_scraping = True
            self.__condition_variable.notify()
            self.__condition_variable.release()
            
            self.logger.info("stop signal received, joining scraper...")
            self.timelineScraperThread.join()
        self.logger.info("stopped, see you next time!")        

    def __threadLoop(self):
        self.__condition_variable.acquire()
        while not self.__stop_scraping:
            try:
                # build the request
                self.logger.info('building request for "%s" with status: %s' % 
                    (self._name,
                    str(self._status) 
                ))

                # returns results whose id is greater than request_since and lower than or equal to request_to
                results = self._engine.get_next(request_since = self._status.request_since, 
                    request_to = self._status.request_to)

                self.logger.info('received answer for "%s" with #Results: %i' % 
                    (self._name ,
                    len(results) 
                ))

                for result in results:
                    self.__storeResult(result)
                
                # If I'm going forward -->| but no new tweets are returned
                if not self._status.request_to and len(results)==0:
                    self.logger.info(
                        "going to sleep because of timeline exhausted")
                    self.__condition_variable.wait(
                        self._engine.seconds_to_wait_after_timeline_exhausted())
                    # continue because it's not necessary to save status
                    continue

                # Else if I'm going forward -->| and some new tweets are returned
                elif not self._status.request_to:
                    # I would like to store the max_id_i_have
                    self._status.max_id_i_have = self._engine.get_max_id_from_last_response()
                    self._status.max_timestamp_i_have = self.engine.get_max_timestamp_from_last_response()

                # If I'm discoverying endless timeline
                if not self._status.request_since:
                    self._status.min_id_i_have = self._engine.get_min_id_from_last_response()
                    self._status.min_timestamp_i_have = self._engine.get_min_timestamp_from_last_response()

                # If I just finished going backward |<--
                if not self._engine.has_next():
                    # Next iteration you must start since current max
                    self._status.request_since = self._status.max_id_i_have
                    self._status.request_since_timestamp = self._status.max_timestamp_i_have
                    
                    # Next iteration should go forward -->
                    self._status.request_to = None
                    self._status.request_to = None 

                    self.__storeStatus()
                    self.logger.info("going to sleep because of timeline exhausted")
                    self.__condition_variable.wait(self._engine.seconds_to_wait_after_timeline_exhausted())
                    continue
                else:
                    # For next requests I would like to use the request_to parameter (i.e. start going backward <--)
                    self._status.request_to = self._engine.get_min_id_from_last_response()-1
                    self._status.request_to_timestamp = self._engine.get_min_timestamp_from_last_response() - 1

                self.__storeStatus()
                self.__condition_variable.wait(0.001)

            except TimelineScraperRateLimitError as e:
                # print(e)
                self.logger.info("going to sleep because of rate limit exceeded" % self._name)
                self.__condition_variable.wait(self._engine.seconds_to_wait_after_rate_limit_exceeded())
            except TimelineScraperError as e:
                self.logger.info("going to sleep because of exception...")
                self.logger.error(e)
                self.__condition_variable.wait(e.seconds_to_wait)
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                self.logger.error("going to sleep because of UNHANDLED exception...")
                self.logger.error(e)
                self.__condition_variable.wait(15*60)
        
        self.__condition_variable.release()

    def __storeResult(self,result):
        # print("TimelineScraper::__storeResult")
        for results_store in self._results_store_list:
            results_store.store_dict_as_json(result)
    
    def __storeStatus(self):
        self._status.save()

    def __str__(self):
        return str(self._status)

    # __dict__ is not the way to go. Use keys and get item
    def as_dict(self):
        return {
            "name" : self._name,
            "engine" : self.engine.__class__.__name__ ,
            'is_alive': self.timelineScraperThread and self.timelineScraperThread.is_alive(),
            "status" : dict(self._status)
        }

# **************************************************************************************************
# TimelineScraper Exceptions
# **************************************************************************************************
class TimelineScraperError(Exception):
    def __init__(self, value, seconds_to_wait = 10*60):
        super(TimelineScraperError, self).__init__()
        self.value = value
        self.seconds_to_wait = seconds_to_wait

    def __str__(self):
        return repr(self.value)

class TimelineScraperRateLimitError(TimelineScraperError):
    def __init__(self, value, seconds_to_wait = 10*60):
        super(TimelineScraperRateLimitError, self).__init__(value, seconds_to_wait)

# **************************************************************************************************
# TimelineScraperStatus
# **************************************************************************************************
class TimelineScraperStatus(object):  

    def __init__(self, timelineScraper, statusDict=None):
        self.timelineScraper = timelineScraper
        
        if not statusDict:
            try:
                name = self.timelineScraper.name
                with open(self.timelineScraper.workspace+"/"+name+'.status.txt', 'r') as infile:
                    statusDict = json.load(infile)   
            except IOError:
                statusDict = {}

        self.max_id_i_have = int(statusDict["max_id_i_have"]) if "max_id_i_have" in statusDict and statusDict["max_id_i_have"] else None
        self.max_timestamp_i_have = statusDict["max_timestamp_i_have"] if "max_timestamp_i_have" in statusDict and statusDict["max_timestamp_i_have"] else None
        
        self.request_to = int(statusDict["request_to"]) if "request_to" in statusDict and statusDict["request_to"] else None
        self.request_to_timestamp = statusDict["request_to_timestamp"] if "request_to_timestamp" in statusDict and statusDict["request_to_timestamp"] else None
        
        self.request_since = int(statusDict["request_since"]) if "request_since" in statusDict and statusDict["request_since"] else None
        self.request_since_timestamp = statusDict["request_since_timestamp"] if "request_since_timestamp" in statusDict and statusDict["request_since_timestamp"] else None

        self.min_id_i_have = int(statusDict["min_id_i_have"]) if "min_id_i_have" in statusDict and statusDict["min_id_i_have"] else None
        self.min_timestamp_i_have = statusDict["min_timestamp_i_have"] if "min_timestamp_i_have" in statusDict and statusDict["min_timestamp_i_have"] else None


    
    def save(self):
        name = self.timelineScraper.name

        # tempFileName and finalFileName are used to make the write operation atomic
        tempFileName = self.timelineScraper.workspace+"/"+name+'.temp.status.txt'
        finalFileName = self.timelineScraper.workspace+"/"+name+'.status.txt'
        with open(tempFileName, 'w') as outfile:
            json.dump(self.as_dict(), outfile)
        os.rename(tempFileName, finalFileName)

    # Utility methods 
    def as_dict(self):
        return {
            'min_id_i_have' : self.min_id_i_have,
            'min_timestamp_i_have': self.min_timestamp_i_have,

            'max_id_i_have': self.max_id_i_have,
            'max_timestamp_i_have': self.max_timestamp_i_have,
            
            'request_to': self.request_to,
            'request_to_timestamp': self.request_to_timestamp,
            
            'request_since': self.request_since,
            'request_since_timestamp': self.request_since_timestamp,
        }
        
    def keys(self):
        return self.as_dict().keys()

    def __getitem__(self,key):
        return self.as_dict()[key]

    def __str__(self):
        return 'request_since:'+str(self.request_since)+' request_to:'+str(self.request_to)+' min_id_i_have:'+str(self.min_id_i_have)+' max_id_i_have:'+str(self.max_id_i_have)
