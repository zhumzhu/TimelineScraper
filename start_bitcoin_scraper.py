import sys
from TimelineScraperManager import create_scraper_from_config

print('Scraper starting...')

rpc_user = sys.argv[1]
rpc_password = sys.argv[2]

config = {
    "name" : "bitcoin_mainnet_scraper",
    
    "engine" : {
        "name" : "BitcoinBlockchainTsEngine",
        'rpcserver_host' : 'localhost',
        'rpcserver_port' : '8332',
        'rpc_user' : rpc_user,
        'rpc_password' : rpc_password,
        'block_batch_size' : 5
    },
    "results_stores" : [
        {
            "name" : "FileSystemResultsStore",
            "rollover_enabled": True,
            "rollover_trigger_size": 10e9
        }
    ]
}

scraper = create_scraper_from_config(config)
scraper.startScraper()

def signal_handler(signal, frame):
    print('Scraper stopping...')
    scraper.stopScraper()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
print('Scraper started! Press Ctrl+C to stop scraper')
signal.pause()