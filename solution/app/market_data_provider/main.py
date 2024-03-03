from abc import ABCMeta

from app.common.user_profiles import UserProfile

maeket_data_providers: dict = dict()


class MarketDataProvider(metaclass=ABCMeta):
    user_profile: UserProfile

    def __init__(self) -> None:
        if hash(self) in maeket_data_providers.keys():
            self = maeket_data_providers[hash(self)]
        else:
            maeket_data_providers[hash(self)] = self
        return

    def __hash__(self) -> int:
        return hash(self.user_profile.user_id + self.user_profile.password)
