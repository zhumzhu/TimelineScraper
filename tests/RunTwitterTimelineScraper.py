import sys,signal,logging
from TimelineScraper import TimelineScraper
from resultstore.FileSystemResultsStore import FileSystemResultsStore
from resultstore.S3ResultsStore import S3ResultsStore
from engines.TwitterTsEngine import TwitterTsEngine
from engines.TradingPlatformsTsEngine import TradingPlatformsTradesTsEngine

workspace = "data"
name = "test_twitter_engine"

from timelinescraper.TimelineScraperManager import create_scraper_from_config

config = {
    "name" : "test_twitter_engine",
    
    "engine" : {
        "name" : "TwitterTsEngine",
        'query' : "us elections",
		'appkey' : "your_app_key", 
		'accesstoken' : "your_access_token"
    },
    "results_stores" : [
        {
            "name" : "FileSystemResultsStore",
            "rollover_enabled": True,
            "rollover_trigger_size": 1e6
        }
    ]
}

scraper = create_scraper_from_config(config)
scraper.logger.setLevel(logging.DEBUG)
scraper.startScraper()

def signal_handler(signal, frame):
    scraper.stopScraper()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop scraper')
signal.pause()
