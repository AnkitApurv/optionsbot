from collections import namedtuple
from typing import Optional

from app.common.class_templates import Singleton

UserProfile = namedtuple("UserProfile", ["platform", "user_id", "password"])
type UserProfileSet = set[UserProfile]


class UserProfiles(Singleton):
    _user_profiles: UserProfileSet

    def __init__(self) -> None:
        # TODO:
        # One platform will have one folder in config parent folder,
        # where one file each will be maintained for one UserProfile
        # this function will be responsible to reading upp all those profile files into _user_profiles
        self._user_profiles.add(UserProfile(platform="a", user_id="b", password="c"))
        self._user_profiles.add(UserProfile(platform="b", user_id="c", password="k"))
        return

    def find_user_profile(
        self, platform: str, user_id: Optional[str]
    ) -> Optional[UserProfile]:
        matched_profiles: UserProfileSet = set(
            filter(
                lambda k: k.platform == platform and k.user_id == user_id,
                self._user_profiles,
            )
        )

        found_profile: Optional[UserProfile] = None
        match matched_profiles.__len__():
            case 0:
                found_profile = None
            case _:
                found_profile = next(iter(matched_profiles))
        return found_profile
