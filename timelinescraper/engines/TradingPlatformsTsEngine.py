import sys
import logging

from timelinescraper.engines.TimelineScraperEngine import TimelineScraperEngine

from timelinescraper.engines.trading_platforms.TradingPlatform import *
from timelinescraper.engines.trading_platforms.Gatecoin import GatecoinTradingPlatform
from timelinescraper.engines.trading_platforms.Bitstamp import BitstampTradingPlatform
from timelinescraper.engines.trading_platforms.Kraken import KrakenTradingPlatform
from timelinescraper.engines.trading_platforms.Poloniex import PoloniexTradingPlatform
from timelinescraper.engines.trading_platforms.TheRockTrading import TheRockTradingTradingPlatform

class TradingPlatformsTsEngine(TimelineScraperEngine):

    def __init__(self, name, platform_name, seconds_to_wait):
        super(TradingPlatformsTsEngine, self).__init__(name)
        self.max_id_from_last_response = None
        self.min_id_from_last_response = None
        self.seconds_to_wait = seconds_to_wait

        print("Creating TradingPlatformsTsEngine with platform_name = %s" % platform_name)
        if platform_name == "bitstamp":
            self.platform = BitstampTradingPlatform(name)
        
        elif platform_name == "kraken":
            self.platform = KrakenTradingPlatform(name)
        
        elif platform_name == "the_rock_trading":
            self.platform = TheRockTradingTradingPlatform(name)
        
        elif platform_name == "poloniex":
            self.platform = PoloniexTradingPlatform(name)

        elif platform_name == "gatecoin":
            self.platform = GatecoinTradingPlatform(name)

        else:
            raise TypeError("Invalid TradingPlatform Name")

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
        return self.seconds_to_wait

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
        return [{"name":"platform_name", "type":"string"},
                {"name": "seconds_to_wait", "type":"int"}]

    def __init__(self, name, platform_name, seconds_to_wait):
        super(TradingPlatformsTradesTsEngine, self).__init__(name, platform_name, seconds_to_wait)

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError
    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("using request_since=%i"%request_since)

        trades = self.platform.get_all_trades()

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
        return [{"name":"platform_name", "type":"String"},
                {"name":"orderbook_depth", "type":"String"}] # TODO: Should be Integer

    def __init__(self, name, platform_name, orderbook_depth):
        self._orderbook_depth = int(orderbook_depth)
        super(TradingPlatformsOrderbookTsEngine, self).__init__(name, platform_name)

    # request_since is the last processed id
    # returns a list of results. Each result is a dict object
    # raises TimelineScraperRateLimitError
    # raises TimelineScraperError

    def get_next(self, request_since = None, request_to = None):
        request_since = 0 if not request_since else request_since
        self.logger.info("get_next with request_since=%i"%request_since)

        orderbooks = self.platform.get_all_orderbooks(self._orderbook_depth)

        self.max_id_from_last_response = orderbooks[0].timestamp
        self.min_id_from_last_response = orderbooks[0].timestamp

        return [o.as_dict() for o in orderbooks]








