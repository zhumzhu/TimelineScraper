import time
from timelinescraper.engines.trading_platforms.TradingPlatform import *

class KrakenTradingPlatform(TradingPlatform):
    def __init__(self,name):
        super(KrakenTradingPlatform, self).__init__(name)
        self.market = "kraken"
        self.market_pairs = {
            TradePair.BTCUSD : ["XBTUSD", "XXBTZUSD"],
            TradePair.BTCEUR : ["XBTEUR", "XXBTZEUR"],
            TradePair.ETHEUR : ["ETHEUR", "XETHZEUR"],
            TradePair.ETHBTC : ["ETHXBT", "XETHXXBT"]
        }

        # https://www.kraken.com/help/api#api-call-rate-limit
        self.time_of_last_reduction = self.int_time_in_seconds()
        self.counter = 0

    def int_time_in_seconds(self):
        return int(time.time())

    def i_can_send_request(self):
        # Tier 2 users have a maximum of 15 and their count gets reduced by 1 every 3 seconds. 
        current_time = self.int_time_in_seconds()
        counter_reduced_by = (current_time - self.time_of_last_reduction)/6
        self.counter = max(self.counter - counter_reduced_by, 0)
        if counter_reduced_by>=1:
            self.time_of_last_reduction = current_time - (current_time - self.time_of_last_reduction)%6

        self.logger.debug("KRAKEN counter reduced by %i, now it's equal to %i" % (counter_reduced_by, self.counter))
        # if the counter exceeds the user's maximum API access is suspended for 15 minutes.
        return self.counter<=5

    def update_counter_after_request(self):
        # Ledger/trade history calls increase the counter by 2.
        self.counter += 2
        self.logger.debug("KRAKEN counter incremented by 2, is now equal to %i" % self.counter)
               

    def get_trades(self, pair=TradePair.BTCUSD):
        trades = []
        market_pair = self._get_market_pair(pair)

        if self.i_can_send_request():
            get_result = self._get_without_error('https://api.kraken.com/0/public/Trades?pair='+market_pair[0])
            trades_json = get_result.json()["result"][market_pair[1]] if get_result else []
            trades = [Trade(
                timestamp = int(trade_json[2]),          
                amount = float(trade_json[1]),
                price = float(trade_json[0]),
                market = self.market,
                pair = pair
                ) for trade_json in trades_json]
            self.update_counter_after_request()
        return trades

    def get_orderbook(self, depth = 15, pair=TradePair.BTCUSD):
        orderbook = Orderbook(
            timestamp = self.int_time_in_seconds(),       
            asks = [],
            bids = [],
            market = self.market,
            pair = pair
        )

        if self.i_can_send_request():
            market_pair = self._get_market_pair(pair)
            get_result = self._get_without_error(
                "https://api.kraken.com/0/public/Depth?pair="+market_pair[0]+"&count="+str(depth))
            orderbook_json = get_result.json()["result"][market_pair[1]] if get_result else {} 
            if orderbook_json:
                orderbook = Orderbook(
                    timestamp = self.int_time_in_seconds(),        
                    asks = [[float(a[0]), float(a[1])] for a in  orderbook_json["asks"]][0:depth],
                    bids = [[float(a[0]), float(a[1])] for a in  orderbook_json["asks"]][0:depth],
                    market = self.market,
                    pair = pair
                )
            self.update_counter_after_request()

        return orderbook