import requests
import time,sys
import logging

from TimelineScraperEngine import TimelineScraperEngine

class Trade:
    def __init__(self,timestamp,amount,price,market):
        self.timestamp = timestamp
        self.amount = amount
        self.price = price
        self.market = market

    def as_dict(self):
        return {
            'timestamp': self.timestamp,
            'amount': self.amount,
            'price': self.price,
            'market': self.market,
        }

    def __str__(self):
        return "%s, %i, %f, %0.4f" % (self.market,self.timestamp,self.amount,self.price)

class Orderbook:
    def __init__(self,timestamp,asks,bids,market):
        self.timestamp = timestamp
        self.asks = asks
        self.bids = bids
        self.market = market

    def as_dict(self):
        return {
            'timestamp' : self.timestamp,
            'asks' : self.asks,
            'bids' : self.bids,
            'market' : self.market
        }

def _get_without_error(url):
    get_result = None
    try:
        get_result = requests.get(url)
    except ConnectionError:
        self.logger.error("_get_without_error notifies ConnectionError")
        get_result = None
    return get_result

# **************************************************************************************************
# Trades
def _poloniex_trades():
    market = "poloniex"
    get_result = _get_without_error('https://poloniex.com/public?command=returnTradeHistory&currencyPair=USDT_BTC')
    trades_json = get_result.json() if get_result else []
    
    trades = [Trade(
        timestamp = int(time.mktime(time.strptime(trade_json["date"], '%Y-%m-%d %H:%M:%S'))),        
        amount = float(trade_json["amount"]),
        price = float(trade_json["rate"]),
        market = market
        ) for trade_json in trades_json]
    return trades

def _bitstamp_trades():
    market = "bitstamp"
    get_result = _get_without_error('https://www.bitstamp.net/api/transactions/')
    trades_json = get_result.json() if get_result else []

    trades = [Trade(
        timestamp = int(trade_json["date"]),
        amount = float(trade_json["amount"]),
        price = float(trade_json["price"]),
        market = market
        ) for trade_json in trades_json]
    return trades

def _the_rock_trading_trades():
    market = "the_rock_trading"
    get_result = _get_without_error('https://api.therocktrading.com/v1/funds/BTCUSD/trades')
    trades_json = get_result.json()["trades"] if get_result else []

    trades = [Trade(
        timestamp = int(time.mktime(time.strptime(trade_json["date"], '%Y-%m-%dT%H:%M:%S.%fZ'))),          
        amount = float(trade_json["amount"]),
        price = float(trade_json["price"]),
        market = market
        ) for trade_json in trades_json]
    return trades

def _gatecoin_trades():
    market = "gatecoin"
    get_result = _get_without_error('https://gatecoin.com/api/Public/Transactions/BTCUSD')
    trades_json = get_result.json()["transactions"] if get_result else [] 
    
    trades = [Trade(
        timestamp = int(trade_json["transactionTime"]),
        amount = float(trade_json["quantity"]),
        price = float(trade_json["price"]),
        market = market
        ) for trade_json in trades_json]
    return trades

def _kraken_trades():
    market = "kraken"
    get_result = _get_without_error('https://api.kraken.com/0/public/Trades?pair=XBTUSD')
    trades_json = get_result.json()["result"]["XXBTZUSD"] if get_result else []
    
    trades = [Trade(
        timestamp = int(trade_json[2]),          
        amount = float(trade_json[1]),
        price = float(trade_json[0]),
        market = market
        ) for trade_json in trades_json]
    return trades

# **************************************************************************************************
# Orderbook
def _poloniex_orderbook(depth=10):
    get_result = _get_without_error(
        'https://poloniex.com/public?command=returnOrderBook&currencyPair=USDT_BTC&depth='+str(depth)
    )
    orderbook_json = get_result.json() if get_result else {}
    
    orderbook = Orderbook(
        timestamp = int(time.time()),        
        asks = [[float(a[0]),a[1]] for a in orderbook_json["asks"]],
        bids = [[float(b[0]),b[1]] for b in orderbook_json["bids"]],
        market = "poloniex"
        )
    return orderbook

def _bitstamp_orderbook(depth=10):
    get_result = _get_without_error(
        'https://www.bitstamp.net/api/order_book/'
    )
    orderbook_json = get_result.json() if get_result else {}

    return Orderbook(
        timestamp = int(orderbook_json["timestamp"]),        
        asks = [[float(a[0]),float(a[1])] for a in orderbook_json["asks"]][0:depth], 
        # Interesting: [0:depth] is resilent to order books shorter than depth.
        # It returns the whole order book as expected!
        bids = [[float(a[0]),float(a[1])] for a in orderbook_json["bids"]][0:depth],
        market = "bitstamp"
        )

def _the_rock_trading_orderbook(depth=10):
    get_result = _get_without_error(
        'https://api.therocktrading.com/v1/funds/BTCUSD/orderbook'
    )
    orderbook_json = get_result.json() if get_result else {}
    
    return Orderbook(
        timestamp = int(time.mktime(time.strptime(orderbook_json["date"][0:-6], '%Y-%m-%dT%H:%M:%S.%f'))),       
        asks = [[float(a["price"]), float(a["amount"])] for a in  orderbook_json["asks"]][0:depth],
        bids = [[float(a["price"]), float(a["amount"])] for a in  orderbook_json["bids"]][0:depth],
        market = "the_rock_trading"
    )

def _gatecoin_orderbook(depth=10):
    get_result = _get_without_error(
        'https://www.gatecoin.com/api/Public/MarketDepth/BTCUSD'
    )
    orderbook_json = get_result.json() if get_result else {}
    
    return Orderbook(
        timestamp = int(time.time()),        
        asks = [[float(a["price"]), float(a["volume"])] for a in  orderbook_json["asks"]][0:depth],
        bids = [[float(a["price"]), float(a["volume"])] for a in  orderbook_json["bids"]][0:depth],
        market = "gatecoin"
    )

def _kraken_orderbook(depth=10):
    get_result = _get_without_error(
        "https://api.kraken.com/0/public/Depth?pair=XBTUSD&count="+str(depth)
    )
    orderbook_json = get_result.json()["result"]["XXBTZUSD"] if get_result else {}

    return Orderbook(
        timestamp = int(time.time()),        
        asks = [[float(a[0]), float(a[1])] for a in  orderbook_json["asks"]][0:depth],
        bids = [[float(a[0]), float(a[1])] for a in  orderbook_json["asks"]][0:depth],
        market = "kraken"
    )

# **************************************************************************************************
# Engine

class TradingPlatformsTsEngine(TimelineScraperEngine):

    def __init__(self):
        super(TradingPlatformsTsEngine, self).__init__()
        self.max_id_from_last_response = None
        self.min_id_from_last_response = None
    
    # Returns True or False
    def has_next(self):
        # could raise TimelineScraperError
        return False

    def get_next(self, request_since = None, request_to = None):
        raise NotImplementedError("TradingPlatformsTsEngine.get_next should be implemented by subclasses!")

    # Returns int
    def get_max_id_from_last_response(self):
        assert self.max_id_from_last_response is not None
        self.logger.debug("get_max_id_from_last_response returning %i"%self.max_id_from_last_response)
        return self.max_id_from_last_response
    
    # Returns int
    def get_min_id_from_last_response(self):
        assert self.min_id_from_last_response is not None
        self.logger.debug("get_min_id_from_last_response returning %i"%self.min_id_from_last_response)
        return self.min_id_from_last_response
        
    # Returns number of seconds
    def seconds_to_wait_after_timeline_exhausted(self):
        return 10

    def seconds_to_wait_after_rate_limit_exceeded(self):
        raise NotImplementedError("Rate Limit is never Exceeded in TradingPlatformsTimelineScraper ")

    # Returns a unix timestamp
    def get_max_timestamp_from_last_response(self):
        return self.get_max_id_from_last_response()

    # Returns a unix timestamp
    def get_min_timestamp_from_last_response(self):
        return self.get_min_id_from_last_response()


class TradingPlatformsTradesTsEngine(TradingPlatformsTsEngine):
    
    @staticmethod
    def get_config_params():
        return [{"name":"name", "type":"String"}]

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError
    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("get_next with request_since=%i"%request_since)

        trades = _poloniex_trades() + _bitstamp_trades() + _the_rock_trading_trades() \
            + _gatecoin_trades() + _kraken_trades()

        filt_sort_trades = sorted(\
            filter(lambda t:t.timestamp>request_since, trades), \
            key = lambda t: t.timestamp, \
            reverse = True)

        self.max_id_from_last_response = filt_sort_trades[0].timestamp if filt_sort_trades else self.max_id_from_last_response
        self.min_id_from_last_response = filt_sort_trades[-1].timestamp if filt_sort_trades else self.max_id_from_last_response

        return [t.as_dict() for t in filt_sort_trades]

class TradingPlatformsOrderbookTsEngine(TradingPlatformsTsEngine):

    def __init__(self, orderbook_depth):
        self._orderbook_depth = int(orderbook_depth)
        super(TradingPlatformsOrderbookTsEngine, self).__init__()

    @staticmethod
    def get_config_params():
        return [{"name":"name", "type":"String"},
                {"name":"orderbook_depth", "type":"String"}] # TODO: Should be Integer

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError
    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("get_next with request_since=%i"%request_since)

        orderbooks = [_poloniex_orderbook(self._orderbook_depth), _bitstamp_orderbook(self._orderbook_depth), 
            _the_rock_trading_orderbook(self._orderbook_depth), _gatecoin_orderbook(self._orderbook_depth), 
            _kraken_orderbook(self._orderbook_depth)]

        self.max_id_from_last_response = orderbooks[0].timestamp
        self.min_id_from_last_response = orderbooks[0].timestamp

        return [o.as_dict() for o in orderbooks]






