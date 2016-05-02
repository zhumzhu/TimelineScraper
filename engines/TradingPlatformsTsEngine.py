import sys
import logging

from TimelineScraperEngine import TimelineScraperEngine

from trading_platforms.TradingPlatform import *
from trading_platforms.Gatecoin import GatecoinTradingPlatform
from trading_platforms.Bitstamp import BitstampTradingPlatform
from trading_platforms.Kraken import KrakenTradingPlatform
from trading_platforms.Poloniex import PoloniexTradingPlatform
from trading_platforms.TheRockTrading import TheRockTradingTradingPlatform

class TradingPlatformsTsEngine(TimelineScraperEngine):

    def __init__(self, name):
        super(TradingPlatformsTsEngine, self).__init__(name)
        self.max_id_from_last_response = None
        self.min_id_from_last_response = None

        self.the_rock_trading = TheRockTradingTradingPlatform(name)
        self.kraken = KrakenTradingPlatform(name)
        self.poloniex = PoloniexTradingPlatform(name)
        self.bitstamp = BitstampTradingPlatform(name)
        self.gatecoin = GatecoinTradingPlatform(name)
        
        self.trading_platforms_list = [
            self.the_rock_trading,
            self.kraken,
            self.poloniex,
            self.bitstamp,
            self.gatecoin
        ]

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
        self.logger.debug("returning %i"%self.min_id_from_last_response)
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
        return []

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError
    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("using request_since=%i"%request_since)

        trades = []
        for tp in self.trading_platforms_list:
            obs = tp.get_all_trades()
            trades.extend(obs)

        '''
        trades = self.poloniex.get_trades(pair = TradePair.BTCUSD) + \
            self.bitstamp.get_trades(pair = TradePair.BTCUSD) + \
            self.the_rock_trading.get_trades(pair = TradePair.BTCUSD) + \
            self.gatecoin.get_trades(pair = TradePair.BTCUSD) + \
            self.kraken.get_trades(pair = TradePair.BTCUSD)
        '''

        # self.logger.debug("trades list %s" % str(trades))

        filt_sort_trades = sorted(\
            filter(lambda t:t.timestamp>request_since, trades), \
            key = lambda t: t.timestamp, \
            reverse = True)

        self.max_id_from_last_response = filt_sort_trades[0].timestamp if filt_sort_trades else self.max_id_from_last_response
        self.min_id_from_last_response = filt_sort_trades[-1].timestamp if filt_sort_trades else self.max_id_from_last_response

        return [t.as_dict() for t in filt_sort_trades]

class TradingPlatformsOrderbookTsEngine(TradingPlatformsTsEngine):

    @staticmethod
    def get_config_params():
        return [{"name":"orderbook_depth", "type":"String"}] # TODO: Should be Integer

    def __init__(self, name, orderbook_depth):
        self._orderbook_depth = int(orderbook_depth)
        super(TradingPlatformsOrderbookTsEngine, self).__init__(name)

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError

    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("get_next with request_since=%i"%request_since)

        orderbooks = []
        for tp in self.trading_platforms_list:
            obs = tp.get_all_orderbooks(self._orderbook_depth)
            orderbooks.extend(obs)

        self.max_id_from_last_response = orderbooks[0].timestamp
        self.min_id_from_last_response = orderbooks[0].timestamp

        return [o.as_dict() for o in orderbooks]

    def get_next_old(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("get_next with request_since=%i"%request_since)

        orderbooks = [
            self.poloniex.get_orderbook(self._orderbook_depth, pair = TradePair.BTCUSD), 
            self.bitstamp.get_orderbook(self._orderbook_depth, pair = TradePair.BTCUSD), 
            self.the_rock_trading.get_orderbook(self._orderbook_depth, pair = TradePair.BTCUSD), 
            self.gatecoin.get_orderbook(self._orderbook_depth, pair = TradePair.BTCUSD), 
            self.kraken.get_orderbook(self._orderbook_depth, pair = TradePair.BTCUSD)]

        self.max_id_from_last_response = orderbooks[0].timestamp
        self.min_id_from_last_response = orderbooks[0].timestamp

        return [o.as_dict() for o in orderbooks]






