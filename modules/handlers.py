from aiogram import Dispatcher, F
from aiogram.enums import ContentType

from modules.url_shortener import UrlShortener, url_input
from modules.get_file_direct_url import get_file_direct_url_handler


def register_handlers(dp: Dispatcher):
    dp.message.register(url_input, UrlShortener.url_prompt)
    dp.message.register(get_file_direct_url_handler, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VIDEO, ContentType.VOICE, ContentType.ANIMATION, ContentType.VIDEO_NOTE}))

