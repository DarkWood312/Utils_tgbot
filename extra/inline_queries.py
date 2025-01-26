import html
import io

import aiohttp
from aiogram import Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InputMediaVideo, \
    BufferedInputFile, InputMediaAudio, InputMediaDocument, InputInvoiceMessageContent, InlineQueryResultVideo, \
    InlineQueryResultCachedVideo, InlineQueryResultAudio, InlineQueryResultDocument
from filetype import filetype

import extra.utils
from extra import config, utils
from extra.config import sql, dl_api_key


async def url_query(inline_query: InlineQuery):
    results = []
    async with aiohttp.ClientSession() as session:
        if config.url_shortener_status:
            results.append(InlineQueryResultArticle(id='url_short', title='Отправить сокращенную ссылку',
                                                    input_message_content=InputTextMessageContent(
                                                        message_text=await utils.shorten_url(inline_query.query,
                                                                                             session))))
        # await inline_query.answer(results, cache_time=10)
        if config.dl_api_key:
            settings = await sql.get_user_settings(inline_query.from_user.id) or {}
            # results.append(InlineQueryResultArticle(id='dl', title='...',
            #                                         input_message_content=InputTextMessageContent(
            #                                             message_text='...'
            #                                         )))
            try:
                content = await utils.download(inline_query.query, dl_api_key, **settings)
                # if content.buffer is not None and content.mimetype.startswith('audio'):
                    # buffer = content.buffer
                    # buffer_val = buffer.read()
                    # caption = utils.format_file_description(content.mimetype, content.filesize_bytes / 1024 / 1024, 'МБ')
                #     match content.mimetype.split('/')[0]:
                #         case 'audio':
                #     result = InlineQueryResultAudio(id='dl', title=html.escape(content.filename), audio_url=content.url, caption=caption)
                #         case 'video':
                #             result = InlineQueryResultVideo(id='dl', title=html.escape(content.filename), video_url=content.url,
                #                                             mime_type=content.mimetype,
                #                                             thumbnail_url='https://files.catbox.moe/u7f0vr.jpg')
                #         case _:
                #             result = InlineQueryResultDocument(id='dl', title=html.escape(content.filename), document_url=content.url,
                #                                                mime_type=content.mimetype)

                # else:
                result = InlineQueryResultArticle(id='dl', title=html.escape(content.filename),
                                                  input_message_content=InputTextMessageContent(
                                                      message_text=f'{await content.get_short_url() or content.url}\n{utils.format_file_description(content.mimetype, content.filesize_bytes / 1024 / 1024, 'МБ', content.filename)}'))

            except utils.DownloadError as e:
                # result = InlineQueryResultArticle(id='dl', title=html.escape(str(e)),
                #                                   input_message_content=InputTextMessageContent(message_text=';('))
                pass

            # results = results[:-1]
            results.append(result)

        await inline_query.answer(results=results, cache_time=0)


async def empty_query(inline_query: InlineQuery):
    if not inline_query.query:
        results = []
        if config.url_shortener_status:
            results.append(
                InlineQueryResultArticle(id='url_short_item', title='>Ссылка для отправки сокращенной ссылки',
                                         input_message_content=InputTextMessageContent(message_text=':)')))
        if config.dl_api_key:
            results.append(
                InlineQueryResultArticle(id='dl_item',
                                         title='>Ссылка на контент для скачивания по настройкам пользователя',
                                         input_message_content=InputTextMessageContent(message_text=':)'))
            )
        await inline_query.answer(results=results)
        return
    await inline_query.answer(results=[])


def register_queries(dp: Dispatcher):
    dp.inline_query.register(url_query, lambda query: bool(utils.match_url(query.query)))
    dp.inline_query.register(empty_query)
