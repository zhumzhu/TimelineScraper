class Asset:
    BTC = "BTC"
    EUR = "EUR"
    ETH = "ETH"
    USD = "USD"
    XMR = "XMR"

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

TradePair.BTCUSD = TradePair(asset = Asset.BTC, currency = Asset.USD).name
TradePair.ETHUSD = TradePair(asset = Asset.ETH, currency = Asset.USD).name

TradePair.BTCEUR = TradePair(asset = Asset.BTC, currency = Asset.EUR).name

TradePair.XMRBTC = TradePair(asset = Asset.XMR, currency = Asset.BTC).name
TradePair.ETHBTC = TradePair(asset = Asset.ETH, currency = Asset.BTC).name

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
    
