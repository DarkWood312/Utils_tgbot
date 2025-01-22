from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
import utils


async def menui() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    if config.dl_api_key:
        markup.row(InlineKeyboardButton(text='Загрузчик', callback_data='menu:downloader'))
    markup.row(InlineKeyboardButton(text='Сокращатель ссылок', callback_data='menu:url_shortener'))
    markup.row(InlineKeyboardButton(text='Прямая ссылка на файл', callback_data='menu:get_file_direct_url'))

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
