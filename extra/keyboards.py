from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from extra import config, utils


def menui() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    if config.dl_api_key:
        markup.row(InlineKeyboardButton(text='Загрузчик', callback_data='menu:downloader'))
    if config.url_shortener_status:
        markup.row(InlineKeyboardButton(text='Сокращатель ссылок', callback_data='menu:url_shortener'))
    if config.get_file_direct_url_status:
        markup.row(InlineKeyboardButton(text='Прямая ссылка на файл', callback_data='menu:get_file_direct_url'))
    # markup.row(InlineKeyboardButton(text='Перевод в другую СС', callback_data='menu:base'))
    markup.row(InlineKeyboardButton(text='CTF Tools', callback_data='menu:ctf_tools'))

    return markup.as_markup()

def ctf_toolsi() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Перевод в другую СС', callback_data='ctf_tools:base'))
    markup.row(InlineKeyboardButton(text='Binwalk', callback_data='ctf_tools:binwalk'))
    markup.row(InlineKeyboardButton(text='Стеганография', callback_data='ctf_tools:steganography'))
    markup.row(InlineKeyboardButton(text='Chepy (аналог Cyberchef)', callback_data='ctf_tools:chepy'))
    markup.row(InlineKeyboardButton(text='Метаданные (exif)', callback_data='ctf_tools:exif'))

    markup.row(to_kbi(button=True))

    return markup.as_markup()

def canceli(button: bool = False) -> InlineKeyboardMarkup | InlineKeyboardButton:
    markup = InlineKeyboardBuilder()
    b = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    if button:
        return b
    markup.row(b)
    return markup.as_markup()


def to_kbi(button: bool = False, callback_data = "menu:menu", text="В меню") -> InlineKeyboardMarkup | InlineKeyboardButton:
    markup = InlineKeyboardBuilder()
    b = InlineKeyboardButton(text=text, callback_data=callback_data)
    if button:
        return b
    markup.row(b)

    return markup.as_markup()

