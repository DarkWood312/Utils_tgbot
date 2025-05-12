import typing
from dataclasses import dataclass, fields, field
from typing import Optional

import aiohttp

from extra.utils import fill_in_dataclass


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

@dataclass(frozen=True)
class FaceitGame:
    game: str
    faceit_elo: str
    game_player_id: str
    game_player_name: str
    region: str
    skill_level: int

@dataclass(frozen=True)
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


class AsyncSteam:
    def __init__(self, api_key: str, session: aiohttp.ClientSession, api_url: str = 'https://api.steampowered.com'):
        self.api_key = api_key
        self.session = session
        self.api_url = api_url

    async def _request(self, path: str, **params) -> dict:
        response = await self.session.get(self.api_url + path, params={'key': self.api_key, **params})
        return (await response.json())['response']


    async def getplayersummaries(self, steamids: list[str] | str) -> list[SteamUser] | None:
        steamids = steamids if isinstance(steamids, str) else ','.join(steamids)

        response = await self._request(f'/ISteamUser/GetPlayerSummaries/v2/', steamids=steamids)
        if len(response['players']) == 0:
            return None

        results = [fill_in_dataclass(user, SteamUser) for user in response['players']]

        return results

    async def search_user(self, username: str) -> SteamUser | None:
        response = await self._request(f'/ISteamUser/ResolveVanityURL/v1/', vanityurl=username)
        if response['success'] != 1:
            return None
        steamid = ['steamid']
        return (await self.getplayersummaries(steamid))[0]

class AsyncFaceit:
    def __init__(self, api_key: str, session: aiohttp.ClientSession, api_url: str = 'https://open.faceit.com'):
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
        response = await self._request(f'/data/v4/players/{faceit_id}')
        return await self._get_player(response, add_friends_field, demon_mode)

    async def get_player_by_steam_id(self, game: str, game_player_id: str, add_friends_field: bool = False, demon_mode: bool = False) -> FaceitUser:
        response = await self._request(f'/data/v4/players', game=game, game_player_id=game_player_id)
        return await self._get_player(response, add_friends_field, demon_mode)