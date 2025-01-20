import logging
import re

import aiohttp
from aiogram import Bot

from aiogram.fsm.context import FSMContext

from constants import bot


async def state_clear(chat_id: int, state: FSMContext, delete_messages: bool = True):
    data = await state.get_data()
    await state.clear()

    if 'delete' in data:
        await bot.delete_messages(chat_id, data['delete'])


async def shorten_url(long_url: str, session: aiohttp.ClientSession):
    async with session.post('https://spoo.me', headers={'Accept': 'application/json'},
                            data={'url': long_url}) as shortener:
        logging.info(await shortener.text())
        short_url = (await shortener.json())['short_url']

    return short_url


def match_url(url: str, with_protocol: bool = True):
    if with_protocol:
        return re.match(r"""^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$""", url, re.IGNORECASE)
    return re.match(
        r"""^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$""",
        url, re.IGNORECASE)
