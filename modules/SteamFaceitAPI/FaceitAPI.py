from datetime import datetime, timedelta

import aiohttp

from .utils import fill_in_dataclass
from .objects.steam import SteamUser
from .objects.faceit.match import *
from .objects.faceit.player import *

class AsyncFaceit:
    def __init__(self, api_key: str, session: aiohttp.ClientSession, api_url: str = 'https://open.faceit.com/data/v4'):
        self.api_key = api_key
        self.session = session
        self.api_url = api_url

    async def _request(self, path: str, **params) -> dict:

        response = await self.session.get(self.api_url + path, params=params, headers={'Authorization': 'Bearer ' + self.api_key})
        return await response.json()

    async def _get_player(self, response: dict, add_friends_field: bool = False, demon_mode: bool = False) -> FaceitUser:
        formatted_data = {}
        for k, v in response.items():
            if k == 'games':
                games = response[k]
                games_results = []
                for game_name in games:
                    g = fill_in_dataclass(games[game_name], FaceitGame, game=game_name)
                    games_results.append(g)
                formatted_data[k] = games_results
            elif k == 'faceit_url':
                formatted_data[k] = v.replace('{lang}', 'ru')
            else:
                formatted_data[k] = v
        if add_friends_field:
            friends_ids = response['friends_ids']
            if len(friends_ids) == 0:
                friends = []
            else:
                friends = [await self.get_player_by_faceit_id(friend_id, demon_mode) for friend_id in friends_ids]
            formatted_data['friends'] = friends
        return fill_in_dataclass(formatted_data, FaceitUser)

    # async def _get_match(self, match: dict):
    #     # match['started_at'] = datetime.fromtimestamp(match['started_at'])
    #     # match['finished_at'] = datetime.fromtimestamp(match['finished_at'])
    #     for game_team_id, team in match['teams'].items():
    #         players = []
    #         for player in team['players']:
    #             players.append(FaceitMatchPlayer(**player))
    #         match['teams'][game_team_id]['players'] = players
    #         # match['teams'][game_team_id]['game_team_id'] = game_team_id
    #     # match['teams'] = [FaceitTeam(**team) for team in match['teams'].values()]
    #     match['teams'] = [fill_in_dataclass(team, FaceitTeam, game_team_id=game_team_id) for game_team_id, team in
    #                       match['teams'].items()]
    #     # match['results'] = FaceitMatchResults(**match['results'])
    #     match['results'] = fill_in_dataclass(match['results'], FaceitMatchResults)


    async def get_player_by_faceit_id(self, faceit_id: str, add_friends_field: bool = False, demon_mode: bool = False):
        response = await self._request(f'/players/{faceit_id}')
        return await self._get_player(response, add_friends_field, demon_mode)

    async def get_player_by_steam_id(self, game: str, game_player_id: str, add_friends_field: bool = False, demon_mode: bool = False) -> FaceitUser:
        response = await self._request(f'/players', game=game, game_player_id=game_player_id)
        return await self._get_player(response, add_friends_field, demon_mode)

    async def get_matches_of_player_by_faceit_id(self, faceit_id: str, game: str, from_: datetime = datetime.now() - timedelta(days=30), to: datetime = datetime.now(), offset: int = 0, limit: int = 20) -> list[FaceitMatchFromPlayer]:
        from_ = from_.timestamp()
        to = to.timestamp()
        response = await self._request(f"/players/{faceit_id}/history", game=game, **{"from": from_} ,to=to, offset=offset, limit=limit)
        matches = []
        for match in response['items']:
            # match['started_at'] = datetime.fromtimestamp(match['started_at'])
            # match['finished_at'] = datetime.fromtimestamp(match['finished_at'])
            for game_team_id, team in match['teams'].items():
                players = []
                for player in team['players']:
                    players.append(FaceitMatchPlayer(**player))
                match['teams'][game_team_id]['players'] = players
                # match['teams'][game_team_id]['game_team_id'] = game_team_id
            # match['teams'] = [FaceitTeam(**team) for team in match['teams'].values()]
            match['teams'] = [fill_in_dataclass(team, FaceitMatchTeamFromPlayer, game_team_id=game_team_id) for game_team_id, team in
                              match['teams'].items()]
            # match['results'] = FaceitMatchResults(**match['results'])
            match['results'] = fill_in_dataclass(match['results'], FaceitMatchResults)

            matches.append(fill_in_dataclass(match, FaceitMatchFromPlayer))

        return matches

    async def get_player_statistics_by_faceit_id(self, faceit_id: str, game: str, offset: int = 0, limit: int = 20, from_: datetime = None, to: datetime = None) -> list[FaceitMatchPlayerStats]:
        if from_:
            from_ = from_.timestamp()
        if to:
            to = to.timestamp()
        params ={k: v for k, v in {
            'offset': offset,
            'limit': limit,
            "from_": from_,
            'to': to}.items() if v is not None}
        response = await self._request(f"/players/{faceit_id}/games/{game}/stats", **params)
        statistics = []
        for match in response['items']:
            match = match['stats']
            statistics.append(FaceitMatchPlayerStats.from_dict(match))
        return statistics

    async def get_match_by_match_id(self, match_id: str) -> FaceitMatchFromMatch:
        match = await self._request(f"/matches/{match_id}")
        for game_team_id, team in match['teams'].items():
            players = []
            for player in team['roster']:
                if 'game_skill_level' in player:
                    player['skill_level'] = player['game_skill_level']

                players.append(fill_in_dataclass(player, FaceitMatchPlayer))
            match['teams'][game_team_id]['players'] = players

            skill_levels = (team['stats']['skillLevel']['average'],
                            team['stats']['skillLevel']['range']['min'],
                            team['stats']['skillLevel']['range']['max'])
            team['stats'] = fill_in_dataclass(team['stats'], FaceitTeamStats, skill_level_avg=skill_levels[0],
                                               skill_level_min=skill_levels[1], skill_level_max=skill_levels[2])


        match['teams'] = [fill_in_dataclass(team, FaceitMatchTeamFromMatch, game_team_id=game_team_id) for game_team_id, team in
                          match['teams'].items()]

        match['results'] = fill_in_dataclass(match['results'], FaceitMatchResults)

        match['map_pick'] = match['voting']['map']['pick']
        match['location_pick'] = match['voting']['location']['pick']

        return fill_in_dataclass(match, FaceitMatchFromMatch)

    async def get_match_stats_by_match_id(self, match_id: str) -> MatchData:
        raw = await self._request(f"/matches/{match_id}/stats")
        rounds: List[Round] = []

        for r in raw["rounds"]:
            # build RoundStats
            rs = RoundStats(
                score=r["round_stats"]["Score"],
                winner=r["round_stats"]["Winner"],
                region=r["round_stats"]["Region"],
                rounds=int(r["round_stats"]["Rounds"]),
                map=r["round_stats"]["Map"],
            )

            teams: List[Team] = []
            for t in r["teams"]:
                ts = t["team_stats"]
                team_stats = TeamStats(
                    first_half_score=int(ts["First Half Score"]),
                    second_half_score=int(ts["Second Half Score"]),
                    final_score=int(ts["Final Score"]),
                    overtime_score=int(ts["Overtime score"]),
                    team_win=bool(ts["Team Win"]),
                    team_headshots=float(ts["Team Headshots"]),
                    team_name=ts["Team"],
                )

                players: List[Player] = []
                for p in t["players"]:
                    ps = p["player_stats"]
                    player_stats = PlayerStats(
                        result=int(ps["Result"]),
                        pistol_kills=int(ps["Pistol Kills"]),
                        one_v_one_wins=int(ps["1v1Wins"]),
                        match_entry_rate=float(ps["Match Entry Rate"]),
                        utility_enemies=int(ps["Utility Enemies"]),
                        k_d_ratio=float(ps["K/D Ratio"]),
                        adr=float(ps["ADR"]),
                        headshots_percent=float(ps["Headshots %"]),
                        utility_damage=int(ps["Utility Damage"]),
                        knife_kills=int(ps["Knife Kills"]),
                        sniper_kill_rate_per_round=float(ps["Sniper Kill Rate per Round"]),
                        kills=int(ps["Kills"]),
                        utility_successes=int(ps["Utility Successes"]),
                        damage=int(ps["Damage"]),
                        flash_successes=int(ps["Flash Successes"]),
                        enemies_flashed=int(ps["Enemies Flashed"]),
                        deaths=int(ps["Deaths"]),
                        flash_success_rate_per_match=float(ps["Flash Success Rate per Match"]),
                        utility_damage_per_round=float(ps["Utility Damage per Round in a Match"]),
                        one_v_one_count=int(ps["1v1Count"]),
                        double_kills=int(ps["Double Kills"]),
                        utility_usage_per_round=float(ps["Utility Usage per Round"]),
                        penta_kills=int(ps["Penta Kills"]),
                        utility_damage_success_rate=float(ps["Utility Damage Success Rate per Match"]),
                        mvps=int(ps["MVPs"]),
                        enemies_flashed_per_round=float(ps["Enemies Flashed per Round in a Match"]),
                        clutch_kills=int(ps["Clutch Kills"]),
                        sniper_kill_rate_per_match=float(ps["Sniper Kill Rate per Match"]),
                        triple_kills=int(ps["Triple Kills"]),
                        entry_count=int(ps["Entry Count"]),
                        quadro_kills=int(ps["Quadro Kills"]),
                        sniper_kills=int(ps["Sniper Kills"]),
                        first_kills=int(ps["First Kills"]),
                        utility_count=int(ps["Utility Count"]),
                        one_v_two_wins=int(ps["1v2Wins"]),
                        one_v_two_count=int(ps["1v2Count"]),
                        flashes_per_round=float(ps["Flashes per Round in a Match"]),
                        zeus_kills=int(ps["Zeus Kills"]),
                        match_one_v_two_win_rate=float(ps["Match 1v2 Win Rate"]),
                        match_entry_success_rate=float(ps["Match Entry Success Rate"]),
                        kr_ratio=float(ps["K/R Ratio"]),
                        utility_success_rate=float(ps["Utility Success Rate per Match"]),
                        entry_wins=int(ps["Entry Wins"]),
                        flash_count=int(ps["Flash Count"]),
                        headshots=int(ps["Headshots"]),
                        match_one_v_one_win_rate=float(ps["Match 1v1 Win Rate"]),
                        assists=int(ps["Assists"])
                    )
                    players.append(Player(
                        player_id=p["player_id"],
                        nickname=p["nickname"],
                        player_stats=player_stats
                    ))

                teams.append(Team(
                    team_id=t["team_id"],
                    premade=bool(t["premade"]),
                    team_stats=team_stats,
                    players=players
                ))

            rounds.append(Round(
                best_of=int(r["best_of"]),
                competition_id=r.get("competition_id"),
                game_id=r["game_id"],
                game_mode=r["game_mode"],
                match_id=r["match_id"],
                match_round=int(r["match_round"]),
                played=int(r["played"]),
                round_stats=rs,
                teams=teams
            ))

        return MatchData(rounds=rounds)

