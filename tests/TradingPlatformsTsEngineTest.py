import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from engines.TradingPlatformsTsEngine import *
import unittest


class TradingPlatformsTsEngineTest(unittest.TestCase):

    def setUp(self):
        self.trades_ts_engine = TradingPlatformsTradesTsEngine("trades_ts_engine_test")
        self.orderbook_ts_engine = TradingPlatformsTradesTsEngine("orderbook_ts_engine_test")

    def test_trades_ts_engine(self):
        trades = self.trades_ts_engine.get_next()
        print trades

    def test_orderbook_ts_engine(self):
        obs = self.orderbook_ts_engine.get_next()
        print obs


if __name__ == '__main__':
    unittest.main()