import time, sys, multiprocessing

from timelinescraper.engines.trading_platforms.Common import *
from timelinescraper.engines.trading_platforms.TradingPlatform import TradingPlatform

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner

poloniex_market_pairs = {
    TradePair.BTCUSD : "USDT_BTC",
    TradePair.ETHUSD : "USDT_ETH",
    TradePair.XRPUSD : "USDT_XRP",
    TradePair.XMRUSD : "USDT_XMR",
    TradePair.LTCUSD : "USDT_LTC",
    TradePair.ETCUSD : "USDT_ETC",
    TradePair.DASHUSD : "USDT_DASH",
    TradePair.ZECUSD : "USDT_ZEC",

    TradePair.ETCETH : "ETH_ETC",
    TradePair.ZECETH : "ETC_ZEC",

    TradePair.ZECXMR  : "XMR_ZEC",
    TradePair.DASHXMR : "XMR_DASH",
    TradePair.LTCXMR  : "XMR_LTC",

    TradePair.ETHBTC : "BTC_ETH",
    TradePair.XMRBTC : "BTC_XMR",
    TradePair.ETCBTC : "BTC_ETC",
    TradePair.LTCBTC : "BTC_LTC",
    TradePair.XRPBTC : "BTC_XRP",
    TradePair.ZECBTC : "BTC_ZEC",
    TradePair.DASHBTC: "BTC_DASH"
}

# Create a queue for each market pair, because we need to return trades
# selectively for each market pair
trades_queue = {k:multiprocessing.Queue() for k in poloniex_market_pairs.keys()}

def on_market_event(market_pair, args, kwargs):
    new_trades = [arg for arg in args if arg["type"] == "newTrade"]
    for t in new_trades:
        # print(market_pair, t)
        trades_queue[market_pair].put(t["data"])

# Here we define the WAMP client
class PoloniexComponent(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):                
        for mp in poloniex_market_pairs.keys():
            # Here we dynamically define specific handlers for each market pair
            exec("def on_{0}(*args, **kwargs): on_market_event('{0}', args, kwargs)"\
                 .format(mp))

            mp_poloniex_name = poloniex_market_pairs[mp]
            yield self.subscribe(locals()['on_'+mp], mp_poloniex_name)

    def onDisconnect(self):
        print("Poloniex Proxy Disconnected")
        if reactor.running:
            reactor.stop()

def run_poloniex_proxy():
    while True:
        print("Running a new Poloniex Proxy")
        sys.stdout.flush()
        
        try:
            runner = ApplicationRunner(url=u"wss://api.poloniex.com", realm=u"realm1")
            runner.run(PoloniexComponent)
        except Exception as e:
            print(e)
            del runner

        sys.stderr.flush()
        sys.stdout.flush()
        time.sleep(2)


# The true TradingPlatform class
class PoloniexTradingPlatform(TradingPlatform):
    def __init__(self,name):
        super(PoloniexTradingPlatform, self).__init__(name)
        self.market = "poloniex"
        self.market_pairs = poloniex_market_pairs
        self.poloniex_proxy_process = multiprocessing.Process(target=run_poloniex_proxy)
        self.poloniex_proxy_process.start()

    def get_trades(self, pair=TradePair.BTCUSD):
        trades_by_trading_platform = []
        q = trades_queue[pair]
        while not q.empty():
            # self.logger.debug("Bitstamp using Proxy, removing from the queue");
            trades_by_trading_platform.append( q.get() )
        
        trades = [Trade(
            timestamp = int(time.mktime(time.strptime(trade_json["date"], '%Y-%m-%d %H:%M:%S'))),        
            amount = float(trade_json["amount"]),
            price = float(trade_json["rate"]),
            market = self.market,
            pair = pair
            ) for trade_json in trades_by_trading_platform]
        return trades

    def get_orderbook(self, depth=15, pair=TradePair.BTCUSD):
        market_pair = self.market_pairs[pair]
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



