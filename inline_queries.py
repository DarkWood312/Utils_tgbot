import aiohttp
from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

import utils
from utils import match_url


async def url_short(inline_query: InlineQuery):
    async with aiohttp.ClientSession() as session:
        await inline_query.answer(results=[
            InlineQueryResultArticle(id='url_short', title='Отправить сокращенную ссылку',
                                     input_message_content=InputTextMessageContent(
                                         message_text=await utils.shorten_url(inline_query.query, session)))])


async def empty_query(inline_query: InlineQuery):
    print(inline_query.query, bool(inline_query.query))
    if not inline_query.query:
        await inline_query.answer(results=[
            InlineQueryResultArticle(id='url_short_item', title='Введите ссылку для отправки сокращенной ссылки',
                                     input_message_content=InputTextMessageContent(message_text=':)'))
        ])
        return
    await inline_query.answer(results=[])


def register_queries(dp: Dispatcher):
    dp.inline_query.register(url_short, lambda query: bool(match_url(query.query)))
    dp.inline_query.register(empty_query)
