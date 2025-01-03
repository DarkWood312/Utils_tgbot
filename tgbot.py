import asyncio
import io
import logging
import os
import re
from pyexpat.errors import messages
from typing import Callable
import magic
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, BufferedInputFile, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from requests import options

from config import *
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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
                    async with session.post(shortener_api_url, headers={'X-Api-Key': dl_api_key}, json={'longUrl': file_url, 'findIfExists': True}) as shortener:
                        short_url = (await shortener.json())['shortUrl']

                    return short_url
                chunk_count += 1

                if callback_status:
                    await callback_status(0, downloaded_size)
        buffer.seek(0)
        if callback_status:
            await callback_status(1, downloaded_size)
        return buffer

@dp.message(CommandStart())
async def commandstart(message: Message):
    if not await sql.get_user(message.from_user.id):
        await sql.add_user(message.from_user.id)
    await message.answer('Просто скинь мне ссылку на видео / аудио файл с ютуба, вк, одноклассников, рутюба, тиктока и др. и я попробую его скачать')

@dp.message(Command(commands='settings'))
async def settings_cmd(message: Message):
    settings = await sql.get_user_settings(message.from_user.id)
    markup = InlineKeyboardBuilder()
    for k, v in settings.items():
        k = str(k)
        v = str(v)
        markup.row(InlineKeyboardButton(text=k, callback_data=k), InlineKeyboardButton(text=v, callback_data=k))
    await message.answer('Настройки: ', reply_markup=markup.as_markup())

@dp.callback_query()
async def callback(call: CallbackQuery):
    settings = await sql.get_user_settings(call.from_user.id)
    if call.data in settings:
        markup = InlineKeyboardBuilder()
        match call.data:
            case 'videoQuality':
                options_ = ['144', '360', '720', '1080', '1440', '2160', '4320', 'max']

            case 'audioFormat':
                options_ = ['best', 'mp3', 'opus', 'ogg', 'wav']

            case 'audioBitrate':
                options_ = ['8', '64', '96', '96', '128', '256', '320']

            case 'filenameStyle':
                options_ = ['classic', 'pretty', 'basic', 'nerdy']


            case 'downloadMode':
                options_ = ['auto', 'audio', 'mute']

            case 'youtubeVideoCodec':
                options_ = ['h264', 'av1', 'vp9']

            case 'youtubeDubLang':
                options_ = ['ru', 'en', '...']

            case 'disableMetadata':
                options_ = ['false', 'true']

            case 'tiktokFullAudio':
                options_ = ['false', 'true']

            case 'tiktokH265':
                options_ = ['false', 'true']

            case 'twitterGif':
                options_ = ['false', 'true']

            case 'youtubeHLS':
                options_ = ['false', 'true']

            case _:
                options_ = []


        for i in options_:
            markup.add(InlineKeyboardButton(text=i, callback_data=f'{call.data}_{i}'))
        await call.message.answer(f'{call.data}: ', reply_markup=markup.as_markup())
    elif any(call.data.startswith(f'{setting}_') for setting in settings):
        setting, value = call.data.split('_', 1)
        if value in ('true', 'false'):
            value = True if value == 'true' else False

        await sql.change_user_setting(call.from_user.id, setting, value)
        await call.message.answer('Успешно!')
    await call.answer()


@dp.message(F.text)
async def text(message: Message):
    args = message.text.split(' ')
    body = args[0]
    if re.match(r"""^[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)$""", body, re.IGNORECASE):
        settings = await sql.get_user_settings(message.from_user.id) or {}
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        try:
            buffer = await download(body, dl_api_key, None, **settings)
        except KeyError:
            await message.answer('какая то ошибка...')
        if isinstance(buffer, io.BytesIO):
            file_type = magic.from_buffer(buffer.read(2048), mime=True)
            buffer.seek(0)
            if len(args) > 0 and ('-d' in args[1:] or '--doc' in args[1:]):
                await message.answer_document(BufferedInputFile(buffer.read(), buffer.name))
                return
            match file_type.split('/', 1)[0]:
                case 'video':
                    await message.answer_video(BufferedInputFile(buffer.read(), buffer.name))
                case 'audio':
                    await message.answer_audio(BufferedInputFile(buffer.read(), buffer.name))
                case _:
                    await message.answer_document(BufferedInputFile(buffer.read(), buffer.name))
        else:
            await message.answer(buffer)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.log(20, "Telegram bot has started!")
    asyncio.run(dp.start_polling(bot))