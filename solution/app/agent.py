from abc import ABCMeta

from app.market_data_provider.main import MarketDataProvider
from app.trading_algorithm.main import TradingAlgorithm
from app.trading_platform.main import TradingPlatform

class TradingAgent(metaclass = ABCMeta):
    trading_algorithm: TradingAlgorithm
    trading_platform: TradingPlatform
    market_data_provider: MarketDataProvider
