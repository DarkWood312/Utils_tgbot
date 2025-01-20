import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from config import token

menu_text = '<b>Меню: </b>'
bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))