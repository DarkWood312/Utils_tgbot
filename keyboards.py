from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def menui() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Downloader', callback_data='menu:downloader'))
    markup.row(InlineKeyboardButton(text='URL shortener', callback_data='menu:url_shortener'))

    return markup.as_markup()


async def canceli() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))

    return markup.as_markup()
