from urlparse import parse_qs
import time
from dateutil import parser

from TimelineScraper import TimelineScraperError, TimelineScraperRateLimitError
from TimelineScraperEngine import TimelineScraperEngine

from twython import Twython
from twython.exceptions import TwythonError, TwythonRateLimitError

class TwitterTsEngine(TimelineScraperEngine):
    
    @staticmethod
    def get_config_params():
        return [{"name":"query", "type":"String"}, 
                {"name":"appkey", "type":"String"},
                {"name":"accesstoken", "type":"String"}]

    def __init__(self, name, query, app_key, access_token):
        super(self.__class__, self).__init__(name)
        
        self._query = query
        self._app_key = app_key
        self._access_token = access_token

        self._count = 100 # 100 is the actual value
        self._twitter_client = Twython(self._app_key, access_token=self._access_token)
           
        self._search_metadata = None
        self._statuses = []

    
    def seconds_to_wait_after_timeline_exhausted(self):
        return 5*60 # 5*60

    def seconds_to_wait_after_rate_limit_exceeded(self):
        return 5*60 # 15*60 is the actual value

    def get_next(self, request_since = None, request_to = None):
        self.logger.debug("TwitterTsEngine is getting next for query "+self._query)
        try:
            results = None
            if not request_since and not request_to:
                results = self._twitter_client.search(q=self._query, count=self._count)
            elif not request_since and request_to:
                results = self._twitter_client.search(q=self._query, count=self._count, max_id=request_to)
            elif request_since and not request_to:
                results = self._twitter_client.search(q=self._query, count=self._count, since_id=request_since)
            else:
                results = self._twitter_client.search(q=self._query, count=self._count, max_id=request_to, since_id=request_since)
            self._search_metadata = results['search_metadata']
            self._statuses = results['statuses']
        except TwythonRateLimitError as e:
            raise TimelineScraperRateLimitError(e)
        except TwythonError as e:
            raise TimelineScraperError(e)

        return self._statuses

    def has_next(self):
        return "next_results" in self._search_metadata

    def get_min_id_from_last_response(self):
        min_id_from_last_response = None
        if "next_results" in self._search_metadata:
            next_results = self._search_metadata['next_results']
            next_results_params = parse_qs(next_results)
            # min_id_from_last_response is the max id of the next request + 1
            min_id_from_last_response = int(next_results_params['?max_id'][0])+1
        elif len(self._statuses):
            ids = [int(status['id']) for status in self._statuses]
            min_id_from_last_response = min(ids)
        
        return min_id_from_last_response

    def get_max_id_from_last_response(self):
        # search_metadata max_id returns the max_id of the status in the response
        # if there are no statuses in the response the max_id is the requested max_id
        return self._search_metadata['max_id']

        # Returns a unix timestamp
    def get_max_timestamp_from_last_response(self):
        return max([time.mktime(parser.parse(t["created_at"]).timetuple()) for t in self._statuses])

    # Returns a unix timestamp
    def get_min_timestamp_from_last_response(self):
        return min([time.mktime(parser.parse(t["created_at"]).timetuple()) for t in self._statuses])

