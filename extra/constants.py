import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from extra import config
from extra.config import token

menu_text = '<b>Меню: </b>'

bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=AiohttpSession(api=TelegramAPIServer.from_base(config.tg_api_server)) if config.tg_api_server else None)
max_file_size_upload = 50 if not config.tg_api_server else 2000
max_file_size_download = 20 if not config.tg_api_server else -1