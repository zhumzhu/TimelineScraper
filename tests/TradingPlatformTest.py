import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from engines.trading_platforms.TradingPlatform import *
import unittest

from engines.trading_platforms.Gatecoin import GatecoinTradingPlatform
from engines.trading_platforms.Bitstamp import BitstampTradingPlatform
from engines.trading_platforms.Kraken import KrakenTradingPlatform
from engines.trading_platforms.Poloniex import PoloniexTradingPlatform
from engines.trading_platforms.TheRockTrading import TheRockTradingTradingPlatform

class TradingPlatformTest(unittest.TestCase):

    def setUp(self):
        self.the_rock_trading = TheRockTradingTradingPlatform("trc")
        self.kraken = KrakenTradingPlatform("krk")
        self.poloniex = PoloniexTradingPlatform("pln")
        self.bitstamp = BitstampTradingPlatform("bts")
        self.gatecoin = GatecoinTradingPlatform("gtc")

    # ******* Structure Checks *******
    def check_trades_structure(self, trades):
        self.assertTrue(isinstance(trades,list))
    
    def check_trade_structure(self, trade):
        self.assertTrue(isinstance(trade,Trade))
        self.assertTrue(isinstance(trade.timestamp,int)) 
        self.assertTrue(isinstance(trade.amount, float))
        self.assertTrue(isinstance(trade.price,float))
        self.assertTrue(isinstance(trade.market,basestring))
        self.assertTrue(isinstance(trade.pair,basestring))

    def check_orderbook_structure(self, orderbook):
        self.assertTrue(isinstance(orderbook,Orderbook))
        self.assertTrue(isinstance(orderbook.timestamp,int)) 
        self.assertTrue(isinstance(orderbook.asks,list)) 
        self.assertTrue(isinstance(orderbook.bids,list)) 
        self.assertTrue(isinstance(orderbook.market,basestring))
        self.assertTrue(isinstance(orderbook.pair,basestring))

    # ******* TheRockTrading *******
    @unittest.skip("")
    def test_the_rock_trading_get_trades(self):
        trades = self.the_rock_trading.get_trades()
        trade = trades[0]
        self.check_trades_structure(trades)
        self.check_trade_structure(trade)
        self.assertEqual(trade.market, "the_rock_trading")
        self.assertEqual(trade.pair, TradePair.BTCUSD)

    @unittest.skip("")
    def test_the_rock_trading_get_orderbook(self):
        orderbook = self.the_rock_trading.get_orderbook()
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.market,"the_rock_trading")
        self.assertEqual(orderbook.pair,TradePair.BTCUSD)
        
    # ******* Kraken *******
    @unittest.skip("")
    def test_kraken_get_trades(self):
        trades = self.kraken.get_trades()
        trade = trades[0]
        self.check_trades_structure(trades)
        self.check_trade_structure(trade)
        self.assertEqual(trade.market, "kraken")
        self.assertEqual(trade.pair, TradePair.BTCUSD)

    @unittest.skip("")
    def test_kraken_get_orderbook(self):
        orderbook = self.kraken.get_orderbook()
        self.assertEqual(orderbook.market,"kraken")
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.pair,TradePair.BTCUSD)

    def test_kraken_get_all_orderbooks(self):
        obs = self.kraken.get_all_orderbooks(depth=15)
        for orderbook in obs: 
            self.assertEqual(orderbook.market,"kraken")
            self.check_orderbook_structure(orderbook)
            # print orderbook

    # ******* Poloniex *******
    @unittest.skip("")
    def test_poloniex_get_trades(self):
        trades = self.poloniex.get_trades()
        trade = trades[0]
        self.check_trades_structure(trades)
        self.check_trade_structure(trade)
        self.assertEqual(trade.market, "poloniex")
        self.assertEqual(trade.pair, TradePair.BTCUSD)

    @unittest.skip("")
    def test_poloniex_get_orderbook(self):
        orderbook = self.poloniex.get_orderbook()
        self.assertEqual(orderbook.market,"poloniex")
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.pair,TradePair.BTCUSD)

    @unittest.skip("")
    # Get all orderbooks
    def test_bitstamp_get_all_orderbooks(self):
        obs = self.poloniex.get_all_orderbooks(depth=15)
        for orderbook in obs: 
            self.assertEqual(orderbook.market,"poloniex")
            self.check_orderbook_structure(orderbook)
            print orderbook

    # ******* Bitstamp *******
    @unittest.skip("")
    def test_bitstamp_get_trades(self):
        trades = self.bitstamp.get_trades()
        trade = trades[0]
        self.check_trades_structure(trades)
        self.check_trade_structure(trade)
        self.assertEqual(trade.market, "bitstamp")
        self.assertEqual(trade.pair, TradePair.BTCUSD)

    @unittest.skip("")
    def test_bitstamp_get_orderbook(self):
        orderbook = self.bitstamp.get_orderbook()
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.market,"bitstamp")
        self.assertEqual(orderbook.pair,TradePair.BTCUSD)

    @unittest.skip("")
    # Get all orderbooks
    def test_bitstamp_get_all_orderbooks(self):
        obs = self.bitstamp.get_all_orderbooks(depth=15)
        for orderbook in obs: 
            self.assertEqual(orderbook.market,"bitstamp")
            self.check_orderbook_structure(orderbook)
            print orderbook

    # ******* Gatecoin *******
    @unittest.skip("")
    def test_gatecoin_get_trades(self):
        trades = self.gatecoin.get_trades()
        trade = trades[0]
        self.check_trades_structure(trades)
        self.check_trade_structure(trade)
        self.assertEqual(trade.market, "gatecoin")
        self.assertEqual(trade.pair, TradePair.BTCUSD)

    @unittest.skip("")
    def test_gatecoin_get_orderbook(self):
        orderbook = self.gatecoin.get_orderbook()
        self.assertEqual(orderbook.market,"gatecoin")
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.pair,TradePair.BTCUSD)

    @unittest.skip("")
    def test_gatecoin_get_orderbook2(self):
        orderbook = self.gatecoin.get_orderbook(depth=15, pair=TradePair.ETHEUR)
        self.assertEqual(orderbook.market,"gatecoin")
        self.check_orderbook_structure(orderbook)
        self.assertEqual(orderbook.pair,TradePair.ETHEUR)

    @unittest.skip("")
    # Get all orderbooks
    def test_gatecoin_get_all_orderbooks(self):
        obs = self.gatecoin.get_all_orderbooks(depth=15)
        for orderbook in obs: 
            self.assertEqual(orderbook.market,"gatecoin")
            self.check_orderbook_structure(orderbook)
            # print orderbook

    @unittest.skip("")
    # Get all trades
    def test_gatecoin_get_all_trades(self):
        trades = self.gatecoin.get_all_trades()
        self.check_trades_structure(trades)
        for t in trades: 
            self.assertEqual(t.market,"gatecoin")
            self.check_trade_structure(t)
            print t


if __name__ == '__main__':
    unittest.main()
