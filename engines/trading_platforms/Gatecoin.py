import time
from TradingPlatform import *

class GatecoinTradingPlatform(TradingPlatform):
    def __init__(self,name):
        super(GatecoinTradingPlatform, self).__init__(name)
        self.market = "gatecoin"
        self.market_pairs = {
            TradePair.BTCUSD : "BTCUSD",
            TradePair.BTCEUR : "BTCEUR",
            TradePair.ETHEUR : "ETHEUR",
            TradePair.ETHBTC : "ETHBTC"
        }

    def get_trades(self, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)

        get_result = self._get_without_error('https://gatecoin.com/api/Public/Transactions/'+market_pair)
        trades_json = get_result.json()["transactions"] if get_result else [] 
        
        trades = [Trade(
            timestamp = int(trade_json["transactionTime"]),
            amount = float(trade_json["quantity"]),
            price = float(trade_json["price"]),
            market = self.market,
            pair = pair
            ) for trade_json in trades_json]
        return trades


    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)
        get_result = self._get_without_error(
            'https://www.gatecoin.com/api/Public/MarketDepth/'+market_pair
        )
        orderbook_json = get_result.json() if get_result else {}

        orderbook = Orderbook(
            timestamp = int(time.time()),        
            asks = [[float(a["price"]), float(a["volume"])] for a in  orderbook_json["asks"]][0:depth],
            bids = [[float(a["price"]), float(a["volume"])] for a in  orderbook_json["bids"]][0:depth],
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