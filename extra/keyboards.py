from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from extra import config, utils


async def menui() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    if config.dl_api_key:
        markup.row(InlineKeyboardButton(text='Загрузчик', callback_data='menu:downloader'))
    if config.url_shortener_status:
        markup.row(InlineKeyboardButton(text='Сокращатель ссылок', callback_data='menu:url_shortener'))
    if config.get_file_direct_url_status:
        markup.row(InlineKeyboardButton(text='Прямая ссылка на файл', callback_data='menu:get_file_direct_url'))
    markup.row(InlineKeyboardButton(text='Перевод в другую СС', callback_data='menu:base'))

    return markup.as_markup()


async def canceli(button: bool = False) -> InlineKeyboardMarkup | InlineKeyboardButton:
    markup = InlineKeyboardBuilder()
    b = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    if button:
        return b
    markup.row(b)
    return markup.as_markup()


async def to_menui(button: bool = False) -> InlineKeyboardMarkup | InlineKeyboardButton:
    markup = InlineKeyboardBuilder()
    b = InlineKeyboardButton(text='В меню', callback_data='menu:menu')
    if button:
        return b
    markup.row(b)

    return markup.as_markup()
