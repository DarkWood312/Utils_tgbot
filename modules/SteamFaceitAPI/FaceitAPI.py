from datetime import datetime, timedelta

import aiohttp

from extra.utils import fill_in_dataclass
from .objects import *

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

    async def get_player_by_faceit_id(self, faceit_id: str, add_friends_field: bool = False, demon_mode: bool = False):
        response = await self._request(f'/players/{faceit_id}')
        return await self._get_player(response, add_friends_field, demon_mode)

    async def get_player_by_steam_id(self, game: str, game_player_id: str, add_friends_field: bool = False, demon_mode: bool = False) -> FaceitUser:
        response = await self._request(f'/players', game=game, game_player_id=game_player_id)
        return await self._get_player(response, add_friends_field, demon_mode)

    async def get_matches_of_player_by_faceit_id(self, faceit_id: str, game: str, from_: datetime = datetime.now() - timedelta(days=30), to: datetime = datetime.now(), offset: int = 0, limit: int = 20) -> list[FaceitMatch]:
        from_ = from_.timestamp()
        to = to.timestamp()
        response = await self._request(f"/players/{faceit_id}/history", game=game, **{"from": from_} ,to=to, offset=offset, limit=limit)
        matches = []
        for match in response['items']:
            match['started_at'] = datetime.fromtimestamp(match['started_at'])
            match['finished_at'] = datetime.fromtimestamp(match['finished_at'])
            for game_team_id, team in match['teams'].items():
                players = []
                for player in team['players']:
                    players.append(FaceitMatchPlayer(**player))
                match['teams'][game_team_id]['players'] = players
                # match['teams'][game_team_id]['game_team_id'] = game_team_id
            # match['teams'] = [FaceitTeam(**team) for team in match['teams'].values()]
            match['teams'] = [fill_in_dataclass(team, FaceitTeam, game_team_id=game_team_id) for game_team_id, team in match['teams'].items()]
            # match['results'] = FaceitMatchResults(**match['results'])
            match['results'] = fill_in_dataclass(match['results'], FaceitMatchResults)
            matches.append(fill_in_dataclass(match, FaceitMatch))

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

    async def get_match_by_match_id(self, match_id: str):
        response = await self._request(f"/matches/{match_id}")
