from dataclasses import dataclass, fields
from datetime import datetime

from ...utils import post_init_wrapper
from typing import *
from .common import FaceitMatchResults, FaceitMatchTeamFromPlayer

@dataclass(frozen=True)
class FaceitGame:
    game: str
    faceit_elo: str
    game_player_id: str
    game_player_name: str
    region: str
    skill_level: int


@dataclass(frozen=True)
@post_init_wrapper
class FaceitUser:
    player_id: str
    nickname: str
    avatar: str
    country: str
    cover_image: str
    faceit_url: str
    friends_ids: list[str]
    games: list[FaceitGame]
    memberships: list[str]
    new_steam_id: str
    platforms: dict[str, str]
    settings: dict
    steam_id_64: str
    steam_nickname: str
    verified: bool
    friends: Optional[list["FaceitUser"]] | None = None

@dataclass(frozen=True)
@post_init_wrapper
class FaceitMatchFromPlayer:
    competition_id: str
    competition_name: str
    competition_type: str
    faceit_url: str
    finished_at: datetime | int
    game_id: str
    game_mode: str
    match_id: str
    match_type: str
    max_players: int
    organizer_id: str
    playing_players: list[str]
    region: str
    results: FaceitMatchResults
    started_at: datetime | int
    status: str
    teams: list[FaceitMatchTeamFromPlayer]
    teams_size: int


@dataclass(frozen=True)
class FaceitMatchPlayerStats:
    first_half_score: int
    kills: int
    overtime_score: int
    quadro_kills: int
    penta_kills: int
    best_of: int
    mvps: int
    team: str
    headshots_percent: float
    map_name: str
    match_round: int
    match_id: str
    adr: float
    kd_ratio: float
    kr_ratio: float
    nickname: str
    result: int
    winner: str
    final_score: int
    rounds: int
    region: str
    game: str
    created_at: datetime | int
    competition_id: str
    player_id: str
    assists: int
    triple_kills: int
    double_kills: int
    game_mode: str
    updated_at: datetime
    headshots: int
    score: str
    deaths: int
    second_half_score: int
    match_finished_at: datetime | int

    @classmethod
    def from_dict(cls, stats: Dict[str, any]) -> "FaceitMatchPlayerStats":
        def _int(k):   return int(stats[k]) if stats.get(k) is not None else 0

        def _float(k): return float(stats[k]) if stats.get(k) is not None else 0.0

        def _iso(k):   return datetime.fromisoformat(stats[k].replace("Z", "+00:00"))

        def _ms(k):
            if isinstance(stats[k], int):
                return datetime.fromtimestamp(stats[k] / 1000.0)
            return stats[k]

        return cls(
            first_half_score=_int("First Half Score"),
            kills=_int("Kills"),
            overtime_score=_int("Overtime score"),
            quadro_kills=_int("Quadro Kills"),
            penta_kills=_int("Penta Kills"),
            best_of=_int("Best Of"),
            mvps=_int("MVPs"),
            team=stats.get("Team", ""),
            headshots_percent=_float("Headshots %"),
            map_name=stats.get("Map", ""),
            match_round=_int("Match Round"),
            match_id=stats.get("Match Id", ""),
            adr=_float("ADR"),
            kd_ratio=_float("K/D Ratio"),
            kr_ratio=_float("K/R Ratio"),
            nickname=stats.get("Nickname", ""),
            result=_int("Result"),
            winner=stats.get("Winner", ""),
            final_score=_int("Final Score"),
            rounds=_int("Rounds"),
            region=stats.get("Region", ""),
            game=stats.get("Game", ""),
            created_at=_iso("Created At"),
            competition_id=stats.get("Competition Id", ""),
            player_id=stats.get("Player Id", ""),
            assists=_int("Assists"),
            triple_kills=_int("Triple Kills"),
            double_kills=_int("Double Kills"),
            game_mode=stats.get("Game Mode", ""),
            updated_at=_iso("Updated At"),
            headshots=_int("Headshots"),
            score=stats.get("Score", ""),
            deaths=_int("Deaths"),
            second_half_score=_int("Second Half Score"),
            match_finished_at=_ms("Match Finished At"),
        )
