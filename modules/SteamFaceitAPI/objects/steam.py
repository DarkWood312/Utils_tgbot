from dataclasses import dataclass
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
    lastlogoff: int
    personastate: int
    # personastateflags: bool
    primaryclanid: Optional[str] = None
    timecreated: Optional[int] = None
    gameid: Optional[int] = None
    realname: Optional[str] = None
    gameserverip: Optional[str] = None
    gameextrainfo: Optional[str] = None
    loccityid: Optional[int] = None
    cityid: Optional[int] = None
    loccountrycode: Optional[str] = None
    locstatecode: Optional[str] = None