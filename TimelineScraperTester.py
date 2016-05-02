import sys,signal,logging
from TimelineScraper import TimelineScraper
from resultstore.FileSystemResultsStore import FileSystemResultsStore
from resultstore.S3ResultsStore import S3ResultsStore
from engines.TwitterTsEngine import TwitterTsEngine
from engines.TradingPlatformsTsEngine import TradingPlatformsTradesTsEngine

workspace = "data"
name = "test_twitter_engine"

scraper = TimelineScraper(name = name, workspace = workspace)
scraper.logger.setLevel(logging.DEBUG)
scraper.engine = TwitterTsEngine(
	name = name, 
	query = "bitcoin", 
	app_key = "qVRt030H3uyC5NH9ZAqoKh15S", 
	access_token = "AAAAAAAAAAAAAAAAAAAAAF%2F8bwAAAAAAugy0B%2BK40gKjn0YsNnT%2BgqnmeYM%3DSaul4cnSMzUa0stBXTIB6ab1TetJjclTnmenLXtpcwHf0vNUhb"
)
# scraper.engine = TradingPlatformsTradesTsEngine(name = name)
# scraper.results_store = FileSystemResultsStore(
# 	name = name,
# 	workspace = workspace, 
# 	rollover_enabled = True, 
# 	rollover_trigger_size = 1e6
# )

scraper.results_store = S3ResultsStore(
	name = name, 
	workspace = workspace, 
	rollover_enabled = True, 
	rollover_trigger_size = 1e6
)

scraper.startScraper()

def signal_handler(signal, frame):
    scraper.stopScraper()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop scraper')
signal.pause()
