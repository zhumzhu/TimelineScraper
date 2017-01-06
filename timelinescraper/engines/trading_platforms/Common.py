class Token:
    BTC = "BTC"
    EUR = "EUR"
    ETH = "ETH"
    ETC = "ETC"
    USD = "USD"
    XRP = "XRP"
    XMR = "XMR"
    ZEC = "ZEC"
    LTC = "LTC"
    DASH = "DASH"

class TradePair:
    def __init__(self, asset, currency):
        self.asset = asset
        self.currency = currency

    @property
    def name(self):
        return str(self)

    def __str__(self):
        return '%s%s'%(self.asset,self.currency)

    def __repr__(self):
        return {'currency':self.currency, 'asset':self.asset}

TradePair.BTCUSD = TradePair(asset = Token.BTC, currency = Token.USD).name
TradePair.ETHUSD = TradePair(asset = Token.ETH, currency = Token.USD).name
TradePair.XRPUSD = TradePair(asset = Token.XRP, currency = Token.USD).name
TradePair.XMRUSD = TradePair(asset = Token.XMR, currency = Token.USD).name
TradePair.LTCUSD = TradePair(asset = Token.LTC, currency = Token.USD).name
TradePair.ETCUSD = TradePair(asset = Token.ETC, currency = Token.USD).name
TradePair.DASHUSD = TradePair(asset = Token.DASH, currency = Token.USD).name
TradePair.ZECUSD = TradePair(asset = Token.ZEC, currency = Token.USD).name

TradePair.BTCEUR = TradePair(asset = Token.BTC, currency = Token.EUR).name
TradePair.BTCEUR = TradePair(asset = Token.BTC, currency = Token.EUR).name
TradePair.ETHEUR = TradePair(asset = Token.ETH, currency = Token.EUR).name
TradePair.XRPEUR = TradePair(asset = Token.XRP, currency = Token.EUR).name
TradePair.XMREUR = TradePair(asset = Token.XMR, currency = Token.EUR).name
TradePair.LTCEUR = TradePair(asset = Token.LTC, currency = Token.EUR).name
TradePair.ETCEUR = TradePair(asset = Token.ETC, currency = Token.EUR).name
TradePair.DASHEUR = TradePair(asset = Token.DASH, currency = Token.EUR).name
TradePair.ZECEUR = TradePair(asset = Token.ZEC, currency = Token.EUR).name

TradePair.ETCETH = TradePair(asset = Token.ETC, currency = Token.ETH).name
TradePair.ZECETH = TradePair(asset = Token.ZEC, currency = Token.ETH).name

TradePair.ZECXMR = TradePair(asset = Token.ZEC, currency = Token.XMR).name
TradePair.DASHXMR = TradePair(asset = Token.DASH, currency = Token.XMR).name
TradePair.LTCXMR = TradePair(asset = Token.LTC, currency = Token.XMR).name

TradePair.ETHBTC = TradePair(asset = Token.ETH, currency = Token.BTC).name
TradePair.XMRBTC = TradePair(asset = Token.XMR, currency = Token.BTC).name
TradePair.ETCBTC = TradePair(asset = Token.ETC, currency = Token.BTC).name
TradePair.LTCBTC = TradePair(asset = Token.LTC, currency = Token.BTC).name
TradePair.XRPBTC = TradePair(asset = Token.XRP, currency = Token.BTC).name
TradePair.ZECBTC = TradePair(asset = Token.ZEC, currency = Token.BTC).name
TradePair.DASHBTC = TradePair(asset = Token.DASH, currency = Token.BTC).name


class TradingPlatform:
    bitstamp = "bitstamp"
    the_rock_trading = "the_rock_trading"
    poloniex = "poloniex"
    kraken = "kraken"

class Trade:
    def __init__(self,timestamp,amount,price,market,pair):
        self.timestamp = timestamp
        self.amount = amount
        self.price = price
        self.market = market
        self.pair = pair

    def as_dict(self):
        return {
            'timestamp': self.timestamp,
            'amount': self.amount,
            'price': self.price,
            'market': self.market,
            'pair' : self.pair
        }

    def __str__(self):
        return "%s, %i, %f, %0.4f" % (self.market,self.timestamp,self.amount,self.price)

class Orderbook:
    def __init__(self,timestamp,asks,bids,market,pair):
        self.timestamp = timestamp
        self.asks = asks
        self.bids = bids
        self.market = market
        self.pair = pair

    def as_dict(self):
        return {
            'timestamp' : self.timestamp,
            'asks' : self.asks,
            'bids' : self.bids,
            'market' : self.market,
            'pair' : self.pair
        }


PlatformPairs = {
    TradingPlatform.bitstamp : [TradePair.BTCUSD]
}
    
