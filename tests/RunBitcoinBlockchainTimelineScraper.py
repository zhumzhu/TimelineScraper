from timelinescraper.TimelineScraperManager import create_scraper_from_config

config = {
    "name" : "blockchain_main_net_scraper",
    
    "engine" : {
        "name" : "BitcoinBlockchainTsEngine",
        'rpcserver_host' : 'localhost',
        'rpcserver_port' : '8332',
        'rpc_user' : 'bitcoin_orpheus',
        'rpc_password' : 'EwJeV3LZTyTVozdECF027BkBMnNDwQaVfakG3A4wXYyk',
        'block_batch_size' : 10
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
    scraper.stopScraper()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to stop scraper')
signal.pause()