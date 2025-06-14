from aiogram import Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram import flags

from modules.Encryption import encrypt_cmd, decrypt_cmd
from modules.ctf_tools.binwalk import binwalk_handler, Binwalk
from modules.ctf_tools.chepytool import chepy_start_handler, ChepyTool, chepy_callback_handler
from modules.ctf_tools.exif import exif_handler, Exif
from modules.ctf_tools.steganography import steganography_handler, Steganography
from modules.url_shortener import UrlShortener, url_input
from modules.get_file_direct_url import get_file_direct_url_handler


def register_handlers(dp: Dispatcher):
    dp.message.register(url_input, UrlShortener.url_prompt, flags={'chat_action': 'typing'})

    dp.message.register(chepy_start_handler, ChepyTool.main, flags={'chat_action': 'typing'})
    dp.callback_query.register(chepy_callback_handler, ChepyTool.main, flags={'chat_action': 'typing'})
    
    dp.message.register(binwalk_handler, Binwalk.wait_for_file, flags={'chat_action': 'typing'})

    dp.message.register(exif_handler, Exif.wait_for_file, flags={'chat_action': 'typing'})

    dp.message.register(steganography_handler, Steganography.wait_for_file, flags={'chat_action': 'typing'})

    dp.message.register(get_file_direct_url_handler, F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VIDEO, ContentType.VOICE, ContentType.ANIMATION, ContentType.VIDEO_NOTE}), flags={'chat_action': 'typing'})

    dp.message.register(encrypt_cmd, Command(commands=['encrypt', 'enc']))
    dp.message.register(decrypt_cmd, Command(commands=['decrypt', 'dec']))