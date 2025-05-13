from dataclasses import dataclass
from ...utils import post_init_wrapper
from typing import *

@dataclass(frozen=True)
class FaceitMatchResults:
    score: dict[str, int]
    winner: str


@dataclass(frozen=True)
@post_init_wrapper
class FaceitMatchPlayer:
    avatar: str
    game_player_id: str
    game_player_name: str
    nickname: str
    player_id: str
    skill_level: int
    faceit_url: Optional[str] = None
    membership: Optional[str] = None

@dataclass(frozen=True)
class FaceitMatchTeamFromPlayer:
    avatar: str
    nickname: str
    players: list[FaceitMatchPlayer]
    team_id: str
    type: str
    game_team_id: Optional[str] = None

