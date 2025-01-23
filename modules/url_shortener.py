import html

import aiohttp
from aiogram.types import Message

from aiogram import Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F

import extra.keyboards
import extra.utils


class UrlShortener(StatesGroup):
    url_prompt = State()


async def url_input(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    if not utils.match_url(message.text):
        msg = await message.answer('<b>Некорректная ссылка!</b>', reply_markup=await keyboards.to_menui())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return
    async with aiohttp.ClientSession() as session:
        short_url = await utils.shorten_url(message.text, session)
        await data['edit'].edit_text(f'{html.escape(message.text)} <b>--></b> {short_url}')
        await utils.state_clear(state, chat_id=message.chat.id)
