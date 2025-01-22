import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from dotenv import load_dotenv

import config
from config import token

menu_text = '<b>Меню: </b>'

bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=AiohttpSession(api=TelegramAPIServer.from_base(config.tg_api_server_session)) if config.tg_api_server_session else None)