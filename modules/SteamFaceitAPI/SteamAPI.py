import asyncio


from .objects.steam import SteamUser
import aiohttp

from .utils import fill_in_dataclass
from bs4 import BeautifulSoup




class AsyncSteam:
    def __init__(self, api_key: str, session: aiohttp.ClientSession, api_url: str = 'https://api.steampowered.com'):
        self.api_key = api_key
        self.session = session
        self.api_url = api_url
        self.sessionid = None

    @classmethod
    async def create(cls, api_key: str, session: aiohttp.ClientSession, api_url: str = 'https://api.steampowered.com'):
        self = cls(api_key=api_key, session=session, api_url=api_url)
        self.sessionid = await self._fetch_sessionid()
        return self




    async def _fetch_sessionid(self):
        response = await self.session.get('https://steamcommunity.com')
        if response.status != 200:
            raise Exception(f"Failed to fetch session ID, status code: {response.status}")
        cookies = response.cookies
        return cookies.get('sessionid').value if 'sessionid' in cookies else None

    async def _request(self, path: str, **params) -> dict:
        response = await self.session.get(self.api_url + path, params={'key': self.api_key, **params})
        if response.status != 200:
            error_message = await response.text()
            raise Exception(f"API request failed with status {response.status}: {error_message}")
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
        steamid = response.get('steamid')
        return (await self.getplayersummaries(steamid))[0]

    async def search_users(self, username: str, page: int = 1) -> list[SteamUser]:
        response = await self.session.get("https://steamcommunity.com/search/SearchCommunityAjax"
                                          ,params={
                'text': username, 'filter': 'users', 'sessionid': self.sessionid, 'page': page, 'steamid_user': 'false'
            })
        if response.status != 200:
            raise Exception(f"Failed to search users, status code: {response.status}")
        data = await response.json()
        raw = data.get('html', None)
        soup_users = BeautifulSoup(raw, 'lxml').find_all('div', class_='search_row')
        if not soup_users:
            return []
        user_ids = []
        for soup_user in soup_users:
            user_id = soup_user.find('a', class_='searchPersonaName').get('href').split('/')[-1]
            user_ids.append(user_id)

        return await self.getplayersummaries(user_ids[0])


