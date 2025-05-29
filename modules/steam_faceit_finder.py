import string

import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from modules.SteamFaceitAPI.FaceitAPI import AsyncFaceit

import extra.utils as utils
from extra.config import steam_api_key, faceit_api_key
from modules.SteamFaceitAPI import AsyncSteam
from modules.SteamFaceitAPI.objects.steam import SteamUser


class SteamFaceitFinder(StatesGroup):
    wait_for_info = State()

def is_steamid64(s: str) -> bool:
    if not s.isdigit() or len(s) != 17:
        return False
    sid = int(s)
    return sid >= 76561197960265728

def int_to_base62(n):
    alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
    s = []
    while n:
        n, r = divmod(n, 62)
        s.append(alphabet[r])
    return ''.join(reversed(s)).encode()

def base62_to_int(s):
    alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
    n = 0
    for c in s:
        n = n * 62 + alphabet.index(c)
    return n

async def return_steam_obj(text: str, session: aiohttp.ClientSession) -> SteamUser:
    steam = AsyncSteam(steam_api_key, session)
    if is_steamid64(text):
        return (await steam.getplayersummaries(text))[0]

    username = text
    if utils.match_url(text):
        url = text[:-1] if text[-1] == '/' else text
        username = url.split('/')[-1]

    return await steam.search_user(username)

def make_info_text(init_text = '', **kwargs):
    text = init_text
    for k, v in kwargs.items():
        if v:
            text += f'<b>{k}:</b> {v}\n'

    return text

async def steam_faceit_finder(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        steamobj = await return_steam_obj(message.text, session)
        faceit = AsyncFaceit(faceit_api_key, session)
        kwargs = {
            'Ник': steamobj.personaname,
            'Профиль': 'Открыт✅' if steamobj.profilestate else 'Закрыт❌',
            'Последний раз был в сети': f'{steamobj.lastlogoff:%d-%m-%Y %H:%M:%S}' if steamobj.lastlogoff else None,
            'Статус': steamobj.current_status,
            'Аккаунт был создан': f'{steamobj.timecreated:%d-%m-%Y %H:%M:%S}' if steamobj.timecreated else None,
            'Имя': steamobj.realname,
            'Страна': steamobj.loccountrycode,
            'Город': f'{steamobj.loccityid} | {steamobj.cityid}' if (steamobj.loccityid or steamobj.cityid) else None,
            'IP игрового сервера': steamobj.gameserverip,

            }
        text = make_info_text(f'{steamobj.profileurl}\n')


