from TradingPlatform import *


class BitstampTradingPlatform(TradingPlatform):
    def __init__(self,name):
        super(BitstampTradingPlatform, self).__init__(name)
        self.market = "bitstamp"
        self.market_pairs = {
            TradePair.BTCUSD : "BTCUSD"
        }

    def get_trades(self, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)

        get_result = self._get_without_error('https://www.bitstamp.net/api/transactions/')
        trades_json = get_result.json() if get_result else []

        trades = [Trade(
            timestamp = int(trade_json["date"]),
            amount = float(trade_json["amount"]),
            price = float(trade_json["price"]),
            market = self.market,
            pair = pair
            ) for trade_json in trades_json]
        return trades
        
    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        market_pair = self._get_market_pair(pair)
        get_result = self._get_without_error(
            'https://www.bitstamp.net/api/order_book/'
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