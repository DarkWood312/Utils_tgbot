from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def menui() -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Downloader', callback_data='menu_downloader'))

    return markup.as_markup()