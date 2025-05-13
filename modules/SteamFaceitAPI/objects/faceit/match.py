from dataclasses import dataclass, fields
from datetime import datetime

from ...utils import post_init_wrapper
from typing import *
from .common import FaceitMatchResults, FaceitMatchTeamFromPlayer, FaceitMatchPlayer


@dataclass(frozen=True)
@post_init_wrapper
class FaceitMatchFromMatch:
    match_id: str
    version: int
    game: str
    region: str
    competition_id: str
    competition_type: str
    competition_name: str
    organizer_id: str
    teams: list[FaceitMatchTeamFromPlayer]
    map_pick: list[str]
    location_pick: list[str]
    calculate_elo: bool
    configured_at: int
    started_at: int
    finished_at: int
    demo_url: List[str]
    chat_room_id: str
    best_of: int
    results: FaceitMatchResults
    # detailed_results: List[DetailedResult]
    status: str
    faceit_url: str


    def __post_init__(self):
        if isinstance(self.finished_at, int):
            object.__setattr__(self, "finished_at", datetime.fromtimestamp(self.finished_at))
        if isinstance(self.started_at, int):
            object.__setattr__(self, "started_at", datetime.fromtimestamp(self.started_at))

@dataclass(frozen=True)
class FaceitTeamStats:
    winProbability: float
    rating: int
    skill_level_avg: int
    skill_level_min: int
    skill_level_max: int


@dataclass(frozen=True)
class FaceitMatchTeamFromMatch:
    faction_id: str
    leader: str
    avatar: str
    roster: list[FaceitMatchPlayer]
    stats: FaceitTeamStats
    substituted: bool
    name: str
    type: str
    game_team_id: Optional[str] = None


@dataclass
class RoundStats:
    score: str
    winner: str
    region: str
    rounds: int
    map: str

@dataclass
class PlayerStats:
    result: int
    pistol_kills: int
    one_v_one_wins: int
    match_entry_rate: float
    utility_enemies: int
    k_d_ratio: float
    adr: float
    headshots_percent: float
    utility_damage: int
    knife_kills: int
    sniper_kill_rate_per_round: float
    kills: int
    utility_successes: int
    damage: int
    flash_successes: int
    enemies_flashed: int
    deaths: int
    flash_success_rate_per_match: float
    utility_damage_per_round: float
    one_v_one_count: int
    double_kills: int
    utility_usage_per_round: float
    penta_kills: int
    utility_damage_success_rate: float
    mvps: int
    enemies_flashed_per_round: float
    clutch_kills: int
    sniper_kill_rate_per_match: float
    triple_kills: int
    entry_count: int
    quadro_kills: int
    sniper_kills: int
    first_kills: int
    utility_count: int
    one_v_two_wins: int
    one_v_two_count: int
    flashes_per_round: float
    zeus_kills: int
    match_one_v_two_win_rate: float
    match_entry_success_rate: float
    kd_ratio: float
    utility_success_rate: float
    entry_wins: int
    flash_count: int
    headshots: int
    match_one_v_one_win_rate: float
    assists: int

@dataclass
class Player:
    player_id: str
    nickname: str
    player_stats: PlayerStats

@dataclass
class TeamStats:
    first_half_score: int
    second_half_score: int
    final_score: int
    overtime_score: int
    team_win: bool
    team_headshots: float
    team_name: str

@dataclass
class Team:
    team_id: str
    premade: bool
    team_stats: TeamStats
    players: List[Player]

@dataclass
class Round:
    best_of: int
    competition_id: Optional[str]
    game_id: str
    game_mode: str
    match_id: str
    match_round: int
    played: int
    round_stats: RoundStats
    teams: List[Team]

@dataclass
class MatchData:
    rounds: List[Round]