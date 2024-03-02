from abc import ABCMeta

trading_algorithms: dict = dict()


class TradingAlgorithm(metaclass=ABCMeta):
    algorithm_name: str
    algorithm_version: str

    def __init__(self) -> None:
        if hash(self) in trading_algorithms.keys():
            self = trading_algorithms[hash(self)]
        else:
            trading_algorithms[hash(self)] = self
        return

    def __hash__(self) -> int:
        return hash(self.algorithm_name + self.algorithm_version)
