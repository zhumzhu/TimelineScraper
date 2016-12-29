from timelinescraper.engines.trading_platforms.Poloniex import PoloniexTradingPlatform
import time

poloniex = PoloniexTradingPlatform("my_polo_platform")

time.sleep(20)

print(poloniex.get_trades())