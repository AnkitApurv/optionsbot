from abc import ABCMeta

from app.common.user_profiles import UserProfile

trading_platforms: dict = dict()


class TradingPlatform(metaclass=ABCMeta):
    user_profile: UserProfile

    def __init__(self) -> None:
        if hash(self) in trading_platforms.keys():
            self = trading_platforms[hash(self)]
        else:
            trading_platforms[hash(self)] = self
        return

    def __hash__(self) -> int:
        return hash(self.user_profile.user_id + self.user_profile.password)
