import aiohttp
from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from extra import config, utils

async def url_query(inline_query: InlineQuery):
    results = []
    if config.url_shortener_status:
        async with aiohttp.ClientSession() as session:
            results.append(InlineQueryResultArticle(id='url_short', title='Отправить сокращенную ссылку',
                                                    input_message_content=InputTextMessageContent(
                                                        message_text=await utils.shorten_url(inline_query.query,
                                                                                             session))))
        await inline_query.answer(results=results)


async def empty_query(inline_query: InlineQuery):
    if not inline_query.query:
        results = []
        if config.url_shortener_status:
            results.append(
                InlineQueryResultArticle(id='url_short_item', title='Введите ссылку для отправки сокращенной ссылки',
                                         input_message_content=InputTextMessageContent(message_text=':)')))
        await inline_query.answer(results=results)
        return
    await inline_query.answer(results=[])


def register_queries(dp: Dispatcher):
    dp.inline_query.register(url_query, lambda query: bool(utils.match_url(query.query)))
    dp.inline_query.register(empty_query)
