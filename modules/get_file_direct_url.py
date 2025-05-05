import html
import io
import logging
import sys
import typing
import zipfile

import aiohttp
import filetype
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender

from extra import utils
from extra.constants import bot


async def get_file_direct_url_handler(message: Message):
    cp = message.content_type
    no_name = False
    if cp == 'photo':
        filet = message.photo[-1]
        no_name = True
    elif cp == 'audio':
        filet = message.audio
    elif cp == 'document':
        filet = message.document
    elif cp == 'video':
        filet = message.video
    elif cp == 'video_note':
        filet = message.video_note
        no_name = True
    elif cp == 'voice':
        filet = message.voice
        no_name = True
    elif cp == 'animation':
        filet = message.animation
    else:
        await message.answer('Неизвестный тип файла')
        return

    # await bot.send_chat_action(message.chat.id, 'typing')
    file_size = filet.file_size / 1024 ** 2
    if file_size > 50:
        await message.answer('Невозможно загрузить файл размером больше 50 МБ :(')
        return
    # file_size_text = f'{round(file_size, 2)} МБ' if file_size > 1 else f'{round(file_size * 1024, 2)} КБ'
    file = await bot.download(filet.file_id)
    file_info = await bot.get_file(filet.file_id)
    file_name = filet.file_name if not no_name else file_info.file_path.split('/')[-1]
    msg = await message.answer('<b>Загрузка файла...</b>')
    if file_name[-4:].lower() == '.exe':
        await msg.edit_text('<b>Файл с расширением .exe, архивирование и загрузка...</b>')
        archive_buffer = io.BytesIO()
        archive_buffer.name = f'{file_name[:-4]}.zip'
        with zipfile.ZipFile(archive_buffer, 'w') as archive:
            archive.writestr(file_name, file.read())

        archive_buffer.seek(0)
        file = archive_buffer
        file_name = archive_buffer.name

    async with ChatActionSender.typing(message.chat.id, bot):
        try:

            async with aiohttp.ClientSession() as session:
                direct_link = await get_file_direct_url(file, session, file_name)
            await message.answer(
                f'<b>Прямая ссылка: </b> {html.escape(direct_link)}\n{utils.format_file_description(filetype.guess_mime(file), file_size, 'МБ')}')

        except Exception as e:
            await message.answer(f'error {type(e).__name__} --> {e}', parse_mode=None)

        finally:
            await msg.delete()


# async def get_file_direct_url(file: typing.BinaryIO, session: aiohttp.client.ClientSession, filename: str = None,
#                               expires_in: str | None = None) -> str:
#     form_data = aiohttp.FormData()
#     form_data.add_field('reqtype', 'fileupload')
#     base_url = 'https://catbox.moe/user/api.php'
#     fileb = file.read()
#     file_size = sys.getsizeof(fileb)
#     if expires_in or ((file_size / 1024 ** 2) > 200):
#         base_url = 'https://litterbox.catbox.moe/resources/internals/api.php'
#         form_data.add_field('time', expires_in)
#     form_data.add_field('fileToUpload', fileb, filename=filename or file.name)
#     async with session.post(base_url, data=form_data, headers={
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.771 YaBrowser/23.11.2.771 Yowser/2.5 Safari/537.36'}) as r:
#         logging.info(f'got file direct link {r}')
#         # if not r.status == 200:
#         #     await get_file_direct_link(file, session, filename, expires_in='72h')
#         # else:
#         return await r.text()

async def get_file_direct_url(file: typing.BinaryIO, session: aiohttp.ClientSession = None, filename: str = None) -> str | bool:
    sess = session
    if sess is None:
        sess = aiohttp.ClientSession()
    form_data = aiohttp.FormData()
    base_url = 'https://pomf.lain.la/upload.php'
    fileb = file.read()
    file_size = sys.getsizeof(fileb)
    if file_size / (1024 * 1024) > 2000:
        return False
    form_data.add_field(name='files[]', value=fileb, filename=filename or file.name, content_type=filetype.guess_mime(fileb[:2048]))
    async with sess.post(base_url, data=form_data, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.771 YaBrowser/23.11.2.771 Yowser/2.5 Safari/537.36'}) as r:
        logging.info(f'got file direct link {r}')
        # if not r.status == 200:
        #     await get_file_direct_link(file, sess, filename, expires_in='72h')
        # else:
        rtext = await r.text()
    if not session:
        await sess.close()
    return rtext