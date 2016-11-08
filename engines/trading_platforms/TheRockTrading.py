import time
from timelinescraper.engines.trading_platforms.TradingPlatform import *

class TheRockTradingTradingPlatform(TradingPlatform):
    #limited to 10 requests per second
    def __init__(self, name):
        super(TheRockTradingTradingPlatform, self).__init__(name)
        self.market = "the_rock_trading"
        self.market_pairs = {
            TradePair.BTCUSD : "BTCUSD",
            TradePair.BTCEUR : "BTCEUR"
        }

    def get_trades(self, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)

        get_result = self._get_without_error('https://api.therocktrading.com/v1/funds/'+market_pair+'/trades')
        trades_json = get_result.json()["trades"] if get_result else []

        trades = [Trade(
            timestamp = int(time.mktime(time.strptime(trade_json["date"], '%Y-%m-%dT%H:%M:%S.%fZ'))),          
            amount = float(trade_json["amount"]),
            price = float(trade_json["price"]),
            market = self.market,
            pair = pair
            ) for trade_json in trades_json]
        return trades

    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)

        get_result = self._get_without_error(
            'https://api.therocktrading.com/v1/funds/'+market_pair+'/orderbook'
        )
        orderbook_json = get_result.json() if get_result else {}
        
        orderbook = Orderbook(
            timestamp = int(time.mktime(time.strptime(orderbook_json["date"][0:-6], '%Y-%m-%dT%H:%M:%S.%f'))),       
            asks = [[float(a["price"]), float(a["amount"])] for a in  orderbook_json["asks"]][0:depth],
            bids = [[float(a["price"]), float(a["amount"])] for a in  orderbook_json["bids"]][0:depth],
            market = self.market,
            pair = pair
        ) if orderbook_json else Orderbook(
            timestamp = int(time.time()),       
            asks = [],
            bids = [],
            market = self.market,
            pair = pair
        )

        return orderbook
