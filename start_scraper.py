import sys, json
from TimelineScraperManager import create_scraper_from_config
from pprint import pprint

filename = sys.argv[1]

with open(filename) as data_file:    
    config = json.load(data_file)

print('Scraper starting with config:')
pprint(config)

scraper = create_scraper_from_config(config)
scraper.startScraper()

def signal_handler(signal, frame):
    print('Scraper stopping...')
    scraper.stopScraper()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
print('Scraper started! Press Ctrl+C to stop scraper')
signal.pause()