from aiogram import Dispatcher

from modules.url_shortener import UrlShortener, url_input


def register_handlers(dp: Dispatcher):
    dp.message.register(url_input, UrlShortener.url_prompt)
