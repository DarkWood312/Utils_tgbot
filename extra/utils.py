import html
import io
import logging
import re
from dataclasses import dataclass, field
from typing import *
import aiohttp
import filetype

from aiogram.fsm.context import FSMContext

from extra import constants, config


class DownloadError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@dataclass(frozen=True)
class URLObj:
    url: str
    protocol: str
    host: str
    path: str


@dataclass(frozen=True)
class DownloadedContent:
    url: str
    filename: str
    buffer: io.BytesIO = field(default=None, repr=False)

    @property
    def mimetype(self) -> str | None:
        if self.buffer:
            self.buffer.seek(0)
            mimetype = filetype.guess_mime(self.buffer.read(2048))
            self.buffer.seek(0)

            return mimetype
        return None

    @property
    def filesize_bytes(self) -> int | None:
        if self.buffer:
            self.buffer.seek(0, 2)
            filesize_bytes = self.buffer.tell()
            self.buffer.seek(0)
            return filesize_bytes
        return None

    async def get_short_url(self) -> str:
        async with aiohttp.ClientSession as session:
            return await shorten_url(self.url, session)


async def state_clear(state: FSMContext, delete_messages: bool = True, chat_id: int = None):
    if state is None:
        return
    data = await state.get_data()
    await state.clear()

    if 'delete' in data and delete_messages and chat_id:
        await constants.bot.delete_messages(chat_id, data['delete'])


async def shorten_url(long_url: str, session: aiohttp.ClientSession):
    if not config.url_shortener_status:
        return long_url
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


async def download(url: str, api_key: str, callback_status: Callable = None,
                   **kwargs) -> DownloadedContent:
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

            if data['status'] == 'error':
                raise DownloadError(data['error']['code'])

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
                if downloaded_size > constants.max_file_size_upload * 1024 * 1024:
                    # if return_url_filename_buffer:
                    #     return url, filename, None
                    # return await shorten_url(file_url, session)
                    return DownloadedContent(url=file_url,
                                             filename=filename)
                chunk_count += 1

                if callback_status:
                    await callback_status(0, downloaded_size)
        buffer.seek(0)
        if callback_status:
            await callback_status(1, downloaded_size)
        # if return_url_filename_buffer:
        #     return await shorten_url(file_url, session), filename, buffer
        return DownloadedContent(url=file_url, filename=filename,
                                 buffer=buffer)
        # return buffer


def format_tool_description(name: str, desc: str, extra: str = '') -> str:
    return (f'<b>Название инструмента:</b> <i>{html.escape(name)}</i>\n'
            f'<b>Описание:</b> <i>{html.escape(desc)}</i>'
            f'{extra}')


def format_file_description(file_type: str = None, file_size: int | float = None, file_size_type: str = 'Б'):
    return (f'{f'<b>Тип файла:</b> <code>{html.escape(file_type)}</code>\n' if file_type else ''}'
            f'{f'<b>Размер:</b> <code>{file_size:.2f}</code> <b>{html.escape(file_size_type)}</b>' if file_size else ''}')


def get_url_parts(url: str) -> URLObj:
    parts = re.split(r'^(([^:\/?#]+):)?(\/\/([^\/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?', url)
    return URLObj(url, parts[2], parts[4], parts[5])
