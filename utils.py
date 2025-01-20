import io
import logging
import re
from typing import *
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
        return re.match(
            r"""^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$""",
            url, re.IGNORECASE)
    return re.match(
        r"""^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$""",
        url, re.IGNORECASE)


async def download(url: str, api_key: str, callback_status: Callable = None, **kwargs) -> io.BytesIO | str:
    """

    :param url:
    :param api_key:
    :param callback_status:


    videoQuality: 144, 360, 720, 1080, 1440, 2160, 4320, 'max' -> 1080 \n
    audioFormat: 'best', 'mp3', 'opus', 'ogg', 'wav' -> mp3 \n
    audioBitrate: 320, 256, 128, 96, 64, 8 -> 128\n
    filenameStyle: 'classic', 'pretty', 'basic', 'nerdy' -> classic\n
    downloadMode: 'auto', 'audio', 'mute' -> auto\n
    youtubeVideoCodec: 'h264', 'av1', 'vp9' -> h264\n
    youtubeDubLang: 'ru', 'en' ... -> ru\n
    tiktokFullAudio: -> false\n
    tiktokH265: -> false\n
    twitterGif: -> false\n
    youtubeHLS: -> false\n
    :return: buffer
    """
    async with aiohttp.ClientSession() as session:
        async with session.post('https://dl.dwip.pro',
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                                         'Authorization': f'Api-Key {api_key}'}
                , json={'url': url, **kwargs}) as response:
            data = await response.json()
            logging.info(msg=data)
            file_url = data['url']
            filename = data['filename']
            if callback_status:
                await callback_status(2, 0)
        async with session.get(file_url) as response:
            # total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_count = 0
            chunk_size = 8192  # Adjust chunk size as needed
            buffer = io.BytesIO()
            buffer.name = filename

            async for chunk in response.content.iter_chunked(chunk_size):  # Use iter_any for streaming
                buffer.write(chunk)
                downloaded_size += len(chunk)
                if downloaded_size > 50 * 1024 * 1024:
                    return await shorten_url(file_url, session)
                chunk_count += 1

                if callback_status:
                    await callback_status(0, downloaded_size)
        buffer.seek(0)
        if callback_status:
            await callback_status(1, downloaded_size)
        return buffer
