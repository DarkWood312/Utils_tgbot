from .objects.steam import SteamUser
import aiohttp

from .utils import fill_in_dataclass




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