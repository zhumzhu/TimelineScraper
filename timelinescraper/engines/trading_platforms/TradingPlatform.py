import logging
import requests
import random

from timelinescraper.engines.trading_platforms.Common import Trade, Orderbook

class TradePair(object):
    BTCUSD = "BTCUSD"
    BTCEUR = "BTCEUR"
    ETHEUR = "ETHEUR"
    ETHUSD = "ETHUSD"
    ETHBTC = "ETHBTC"

class NonExistingMarketPair(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message)

class TradingPlatform(object):
    def __init__(self,name):
        self.logger = logging.getLogger(name)

        self.market_pairs = {
            TradePair.BTCUSD : "BTCUSD"
        }

    def get_trades(self, pair=TradePair.BTCUSD):
        raise NotImplementedError("TradingPlatform.get_trades should be implemented by subclasses!")

    def get_orderbook(self, depth, pair=TradePair.BTCUSD):
        raise NotImplementedError("TradingPlatform.get_orderbook should be implemented by subclasses!")

    def get_market_pairs(self):
        # Shuffle market pairs in order to prevent requesting always the same pair because of rate limits
        return random.sample(self.market_pairs.keys(), len(self.market_pairs.keys()))

    def get_all_orderbooks(self,depth):
        orderbooks = []
        for p in self.get_market_pairs():
            orderbooks.append(self.get_orderbook(depth=depth, pair=p))
        return orderbooks

    def get_all_trades(self):
        trades = []
        for p in self.get_market_pairs():
            trades.extend(self.get_trades(pair=p))
        return trades

    def _get_market_pair(self,pair):
        self.logger.warning("TradingPlatform._get_market_pair is deprecated, use direct access to market_pairs dictionary")
        market_pair = None
        if pair in self.market_pairs:
            market_pair = self.market_pairs[pair]
        else:
            raise NonExistingMarketPair(pair)
        return market_pair

    def _get_without_error(self,url):
        get_result = None
        try:
            get_result = requests.get(url, timeout=7)
        except requests.exceptions.ConnectionError:
            self.logger.error("class %s notifies ConnectionError, returning no results" % self.__class__)
            get_result = None
        except requests.exceptions.Timeout:
            self.logger.error("class %s notifies Timeout, returning no results" % self.__class__)
            get_result = None
        return get_result

