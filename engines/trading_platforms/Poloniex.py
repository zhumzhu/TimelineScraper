import time
from TradingPlatform import *


class PoloniexTradingPlatform(TradingPlatform):
    def __init__(self,name):
        super(PoloniexTradingPlatform, self).__init__(name)
        self.market = "poloniex"
        self.market_pairs = {
            TradePair.BTCUSD : "USDT_BTC",
            TradePair.ETHBTC : "BTC_ETH",
            TradePair.ETHUSD : "USDT_ETH"
        }

    def get_trades(self, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)

        get_result = self._get_without_error('https://poloniex.com/public?command=returnTradeHistory&currencyPair='+market_pair)
        trades_json = get_result.json() if get_result else []
        
        trades = [Trade(
            timestamp = int(time.mktime(time.strptime(trade_json["date"], '%Y-%m-%d %H:%M:%S'))),        
            amount = float(trade_json["amount"]),
            price = float(trade_json["rate"]),
            market = self.market,
            pair = pair
            ) for trade_json in trades_json]
        return trades


    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)
        get_result = self._get_without_error(
            'https://poloniex.com/public?command=returnOrderBook&currencyPair='+market_pair+'&depth='+str(depth)
        )
        orderbook_json = get_result.json() if get_result else {}
        
        orderbook = Orderbook(
            timestamp = int(time.time()),        
            asks = [[float(a[0]),a[1]] for a in orderbook_json["asks"]],
            bids = [[float(b[0]),b[1]] for b in orderbook_json["bids"]],
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