from timelinescraper.engines.trading_platforms.TradingPlatform import *

from queue import Queue
import time, threading, json
import pusherclient

class BitstampTradingPlatform(TradingPlatform):
    # Useproxy starts another thread that reads from 
    # websocket APIs
    # Defaults to HTTPs api
    def __init__(self, name, use_proxy = True):
        super(BitstampTradingPlatform, self).__init__(name)
        self.market = "bitstamp"
        self.trading_platform_pairs = {
            TradePair.BTCUSD : {
                'channel' : 'live_trades',
                'trades_url' : 'https://www.bitstamp.net/api/v2/transactions/btcusd/', 
                'obook_url' : 'https://www.bitstamp.net/api/v2/order_book/btcusd/',
                'trades_queue' : None, # Data structure used by proxy to push trades
                'obook_queue' : None
            },
            TradePair.BTCEUR : {
                'channel' : 'live_trades_btceur',
                'trades_url': 'https://www.bitstamp.net/api/v2/transactions/btceur/',
                'obook_url': 'https://www.bitstamp.net/api/v2/order_book/btceur/',
                'trades_queue' : None,
                'obook_queue' : None
            }
        }
        self.market_pairs = self.trading_platform_pairs

        # Proxy configuration
        self.use_proxy = use_proxy
        if use_proxy:
            for p in self.trading_platform_pairs:
                self.trading_platform_pairs[p]['trades_queue'] = Queue()
                self.trading_platform_pairs[p]['obook_queue'] = Queue()
            
            # Last orderbook received by proxy
            self.current_orderbook = {}

            proxy_thread = threading.Thread(
                target = self.__proxy_start, 
                name="BitstampTradingPlatformProxy")

            # The entire Python program exits when no alive non-daemon threads are left.
            proxy_thread.daemon = True
            proxy_thread.start()  


    def __proxy_start(self):
        def on_BTCUSD_trade_received(message):
            # self.logger.debug("Bitstamp Proxy, message received: %s" % message);
            t = json.loads(message)
            # websocket has timestamp, rest has date
            t['date'] = t['timestamp']
            
            self.trading_platform_pairs[TradePair.BTCUSD]['trades_queue'].put(t)

        def on_BTCEUR_trade_received(message):
            # self.logger.debug("Bitstamp Proxy, message received: %s" % message);
            t = json.loads(message)
            # websocket has timestamp, rest has date
            t['date'] = t['timestamp']
            self.trading_platform_pairs[TradePair.BTCEUR]['trades_queue'].put(t)

        def on_BTCUSD_obook_received(message):
            # self.logger.debug("Bitstamp Proxy, message received: %s" % message);
            o = json.loads(message)
            o['timestamp'] = int(time.time()) # obook from websocket doesn't have timestamp!
            self.trading_platform_pairs[TradePair.BTCUSD]['obook_queue'].put(o)

        def on_BTCEUR_obook_received(message):
            # self.logger.debug("Bitstamp Proxy, message received: %s" % message);
            o = json.loads(message)
            o['timestamp'] = int(time.time())
            self.trading_platform_pairs[TradePair.BTCEUR]['obook_queue'].put(o)

        def on_connect(data):
            self.logger.debug("Bitstamp Proxy, connected!");
            self.pusher.subscribe('live_trades').bind('trade', on_BTCUSD_trade_received)
            self.pusher.subscribe('order_book').bind('data', on_BTCUSD_obook_received)
            self.pusher.subscribe('live_trades_btceur').bind('trade', on_BTCEUR_trade_received)
            self.pusher.subscribe('order_book_btceur').bind('data', on_BTCEUR_obook_received)

        # https://it.bitstamp.net/websocket/
        self.logger.debug("BitstampTradingPlatform Proxy is starting");
        self.pusher = pusherclient.Pusher('de504dc5763aeef9ff52')
        self.pusher.connection.logger.setLevel(logging.ERROR)
        self.pusher.connection.bind('pusher:connection_established', on_connect)
        self.pusher.connect()

        # get the first trades
        for p in self.trading_platform_pairs:
            url =  self.trading_platform_pairs[p]['trades_url'] 
            get_result = self._get_without_error(url)
            for t in (get_result.json() if get_result else []):
                self.trading_platform_pairs[p]['trades_queue'].put(t)

        # get the first orderbook
        for p in self.trading_platform_pairs:
            url = self.trading_platform_pairs[p]['obook_url']
            get_result = self._get_without_error(url)
            orderbook_json = get_result.json() if get_result else {}
            self.trading_platform_pairs[p]['obook_queue'].put(orderbook_json)

        while True:
            # Do other things in the meantime here...
            time.sleep(0.1)
        
    def get_trades(self, pair=TradePair.BTCUSD):
        trades_by_trading_platform = None
        if self.use_proxy:
            trades_by_trading_platform = []
            trades_queue = self.trading_platform_pairs[pair]['trades_queue']
            while not trades_queue.empty():
                # self.logger.debug("Bitstamp using Proxy, removing from the queue");
                trades_by_trading_platform.append( trades_queue.get() )
        else:
            get_result = self._get_without_error('https://www.bitstamp.net/api/transactions/')
            trades_by_trading_platform = get_result.json() if get_result else []

        trades = [Trade(
            timestamp = int(t["date"]),
            amount = float(t["amount"]),
            price = float(t["price"]),
            market = self.market,
            pair = pair
            ) for t in trades_by_trading_platform]
        return trades
        
    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        orderbook_json = None
        
        if self.use_proxy:
            obook_queue = self.trading_platform_pairs[pair]['obook_queue']
            while not obook_queue.empty():
                self.current_orderbook =  obook_queue.get()
            orderbook_json = self.current_orderbook
        else:
            get_result = self._get_without_error(
                self.trading_platform_pairs[pair]['obook_url']
            )
            orderbook_json = get_result.json() if get_result else {}

        orderbook = Orderbook(
            timestamp = int(orderbook_json["timestamp"]),        
            asks = [[float(a[0]),float(a[1])] for a in orderbook_json["asks"]][0:depth], 
            # Interesting: [0:depth] is resilent to order books shorter than depth.
            # It returns the whole order book as expected!
            bids = [[float(a[0]),float(a[1])] for a in orderbook_json["bids"]][0:depth],
            market = "bitstamp",
            pair = pair
        ) if orderbook_json else Orderbook(
            timestamp = int(time.time()),       
            asks = [],
            bids = [],
            market = self.market,
            pair = pair
        )

        return orderbook