from dataclasses import dataclass
from datetime import datetime
from typing import *

@dataclass(frozen=True)
class SteamUser:
    steamid: str
    communityvisibilitystate: int
    profilestate: bool
    personaname: str
    commentpermission: bool
    profileurl: str
    avatar: str
    avatarmedium: str
    avatarfull: str
    avatarhash: str
    lastlogoff: datetime | int
    personastate: int | str
    # personastateflags: bool
    primaryclanid: Optional[str] = None
    timecreated: Optional[int | datetime] = None
    gameid: Optional[int] = None
    realname: Optional[str] = None
    gameserverip: Optional[str] = None
    gameextrainfo: Optional[str] = None
    loccityid: Optional[int] = None
    cityid: Optional[int] = None
    loccountrycode: Optional[str] = None
    locstatecode: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.lastlogoff, int):
            object.__setattr__(self, 'lastlogoff', datetime.fromtimestamp(self.lastlogoff))
        if isinstance(self.timecreated, int):
            object.__setattr__(self, 'timecreated', datetime.fromtimestamp(self.timecreated))

    @property
    def username(self):
        return self.profileurl.split('/')[-2]

    @property
    def current_status(self):
        match self.personastate:
            case 0:
                return 'offline'
            case 1:
                return 'online'
            case 2:
                return 'busy'
            case 3:
                return 'away'
            case 4:
                return 'snooze'
            case 5:
                return 'looking for trade'
            case 6:
                return 'looking to play'
            case _:
                return None