import asyncio
import html
import io
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatAction
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import Message, InlineKeyboardButton, BufferedInputFile, CallbackQuery, Update, InlineKeyboardMarkup, \
    InlineQuery, InlineQueryResult, InlineQueryResultArticle, InputMessageContent, InputTextMessageContent, \
    InputMediaDocument, InputMediaVideo, InputMediaAudio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filetype import filetype

from extra.constants import bot, menu_text
import extra.keyboards as kb
from extra.config import *
from extra import utils, config, constants
from extra.inline_queries import register_queries
from extra.middlewares import register_middlewares
from modules.handlers import register_handlers
from modules.url_shortener import UrlShortener
from extra.utils import match_url, format_file_description

dp = Dispatcher(storage=MemoryStorage())

register_middlewares(dp)
register_queries(dp)


@dp.message(CommandStart())
async def commandstart(message: Message, state: FSMContext):
    await utils.state_clear(state, chat_id=message.chat.id)
    if not await sql.get_user(message.from_user.id):
        await sql.add_user(message.from_user.id)
    # await message.answer(
    #     'Просто скинь мне ссылку на видео / аудио файл с ютуба, вк, одноклассников, рутюба, тиктока и др. а я попробую его скачать')
    await message.answer(menu_text, reply_markup=await kb.menui())


# @dp.message(Command(commands='settings'))
# async def settings_cmd(message: Message):
#     settings = await sql.get_user_settings(message.from_user.id)
#     markup = InlineKeyboardBuilder()
#     for k, v in settings.items():
#         k = str(k)
#         v = str(v)
#         markup.row(InlineKeyboardButton(text=k, callback_data=k), InlineKeyboardButton(text=v, callback_data=k))
#     await message.answer('Настройки: ', reply_markup=markup.as_markup())

@dp.message(Command(commands=['short_url', 'su', 'url']))
async def short_url_cmd(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            f'<b>Использование: </b><code>/{command.command} {html.escape("<ссылка для сокращения>")}</code>')
        return
    args = command.args.split(' ')
    long_url = args[0]
    if not utils.match_url(long_url):
        await message.answer('<b>Некорректная ссылка!</b>')
        return

    async with aiohttp.ClientSession() as session:
        short_url = await utils.shorten_url(long_url, session)

    await message.answer(short_url)


@dp.message(Command(commands='get_state'))
async def get_state_cmd(message: Message, state: FSMContext):
    await message.answer(f'state: {await state.get_state() or None}\n')
    # f'state_data {await state.get_data() or None}')


@dp.callback_query(F.data == 'cancel')
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await utils.state_clear(state, chat_id=call.message.chat.id)
    if 'edit' in data and 'to_kwargs' in data:
        await data['edit'].edit_text(**data['to_kwargs'])
    else:
        await call.message.edit_text(menu_text, reply_markup=await kb.menui())
    await call.answer()


register_handlers(dp)


@dp.callback_query()
async def callback(call: CallbackQuery, state: FSMContext):
    settings = await sql.get_user_settings(call.from_user.id)
    if call.data in settings:
        markup = InlineKeyboardBuilder()
        match call.data:
            case 'videoQuality':
                options_ = ['144', '360', '720', '1080', '1440', '2160', '4320', 'max']

            case 'audioFormat':
                options_ = ['best', 'mp3', 'opus', 'ogg', 'wav']

            case 'audioBitrate':
                options_ = ['8', '64', '96', '96', '128', '256', '320']

            case 'filenameStyle':
                options_ = ['classic', 'pretty', 'basic', 'nerdy']

            case 'downloadMode':
                options_ = ['auto', 'audio', 'mute']

            case 'youtubeVideoCodec':
                options_ = ['h264', 'av1', 'vp9']

            case 'youtubeDubLang':
                options_ = ['ru', 'en', '...']

            case 'disableMetadata':
                options_ = ['false', 'true']

            case 'tiktokFullAudio':
                options_ = ['false', 'true']

            case 'tiktokH265':
                options_ = ['false', 'true']

            case 'twitterGif':
                options_ = ['false', 'true']

            case 'youtubeHLS':
                options_ = ['false', 'true']

            case _:
                options_ = []

        for i in options_:
            markup.add(InlineKeyboardButton(text=i, callback_data=f'{call.data}:{i}'))
        await call.message.answer(f'{call.data}: ', reply_markup=markup.as_markup())
    elif any(call.data.startswith(f'{setting}:') for setting in settings):
        setting, value = call.data.split(':', 1)
        if value in ('true', 'false'):
            value = True if value == 'true' else False

        await sql.change_user_setting(call.from_user.id, setting, value)
        await call.answer('Успешно!')
    elif call.data.startswith('menu:'):
        setting, value = call.data.split(':', 1)
        match value:
            case 'menu':
                await utils.state_clear(state, chat_id=call.message.chat.id)
                await call.message.edit_text(menu_text)
                await call.message.edit_reply_markup(reply_markup=await kb.menui())
            case 'downloader':
                downloader_markup = InlineKeyboardBuilder()
                downloader_markup.row(InlineKeyboardButton(text='Настройки: ', callback_data='downloader:settings'))
                downloader_markup.row(await kb.to_menui(True))
                await call.message.edit_text(utils.format_tool_description('Загрузчик',
                                                                           'Скиньте мне ссылку на видео / аудио файл с ютуба, вк, одноклассников, рутюба, тиктока и др. а я попробую его скачать'),
                                             reply_markup=downloader_markup.as_markup())

            case 'url_shortener':
                msg = await call.message.edit_text(
                    utils.format_tool_description('Сокращатель ссылок', 'Отправьте ссылку, которую нужно сократить'),
                    reply_markup=await kb.to_menui())
                await state.set_state(UrlShortener.url_prompt)
                await state.update_data({'edit': msg})

            case 'get_file_direct_url':
                await call.message.edit_text(utils.format_tool_description('Прямая ссылка на файл',
                                                                           f'Отправьте файл (<{1000 if constants.max_file_size_download == -1 else constants.max_file_size_download} МБ) для получения прямой ссылки на него.'),
                                             reply_markup=await kb.to_menui())


    elif call.data.startswith('downloader:'):
        setting, value = call.data.split(':', 1)
        match value:
            case 'settings':
                settings = await sql.get_user_settings(call.from_user.id)
                markup = InlineKeyboardBuilder()
                for k, v in settings.items():
                    k = str(k)
                    v = str(v)
                    markup.row(InlineKeyboardButton(text=k, callback_data=k),
                               InlineKeyboardButton(text=v, callback_data=k))
                markup.row(InlineKeyboardButton(text='Назад', callback_data='menu:downloader'))
                await call.message.edit_text('<b>Настройки: </b>', reply_markup=markup.as_markup())

    await call.answer()


@dp.message(F.text)
async def text(message: Message):
    buffer = None
    args = message.text.split(' ')
    body = args[0]
    if utils.match_url(body):
        settings = await sql.get_user_settings(message.from_user.id) or {}
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        try:
            msg = await message.answer('<b>Скачивание...</b>')
            buffer = await utils.download(body, dl_api_key, None, **settings)
            if isinstance(buffer, io.BytesIO):
                file_type = filetype.guess_mime(buffer.read(2048))
                msg = await msg.edit_text(f'<b>Файл скачан! Отправка...</b>\n<b>Тип файла: </b> {file_type}')
                buffer.seek(0, 2)
                file_size = buffer.tell()
                buffer.seek(0)
                buffer_val = buffer.read()
                file_typec = file_type
                caption = format_file_description(file_type, file_size / 1024 / 1024, 'МБ')
                if len(args) > 0 and ('-d' in args[1:] or '--doc' in args[1:]):
                    file_typec = 'doc/doc'
                match file_typec.split('/', 1)[0]:
                    case 'video':
                        await message.answer_video(BufferedInputFile(buffer_val, buffer.name), caption=caption)
                    case 'audio':
                        await message.answer_audio(BufferedInputFile(buffer_val, buffer.name), caption=caption)
                    case _:
                        await message.answer_document(BufferedInputFile(buffer_val, buffer.name), caption=caption)

                await msg.delete()
            else:
                await msg.edit_text(f'{buffer}')
        except utils.DownloadError as e:
            if str(e) == 'error.api.content.video.unavailable':
                await message.answer(f'Видео недоступно :(. Скорее всего оно имеет возрастное ограничение')
            return
        except Exception as e:
            await message.answer(f'error {html.escape(type(e).__name__)} {html.escape(str(e))}')
            return


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    if config.tg_api_server:
        logging.info(f'Using own {config.tg_api_server} telegram api url. Limits are increased.')
    logging.log(20, "Telegram bot has started!")
    asyncio.run(main())
