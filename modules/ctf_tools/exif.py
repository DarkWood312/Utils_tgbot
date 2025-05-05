import html
from typing import Any
from extra import utils
import exifread
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from extra import keyboards
from extra.constants import bot


class Exif(StatesGroup):
    wait_for_file = State()

def format_exif_data(raw: dict[str, Any], text_formatting = True):
    if text_formatting:
        return "\n".join(f"<b>{html.escape(str(k))}</b>: <code>{html.escape(str(v))}</code>" for k, v in raw.items())
    return "\n".join(f"{str(k)}: {str(v)}" for k, v in raw.items())



async def exif_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.document:
        msg = await message.answer('<b>Отправьте боту фото как файл!</b>', reply_markup=await keyboards.to_kbi())
        await state.update_data(
            {'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return
    fileobj = message.document


    file = await bot.download(fileobj)
    exif_data = exifread.process_file(file)
    formatted = format_exif_data(exif_data)

    if not formatted:
        await message.answer('<b>В файле не было найдено метаданных</b>', reply_markup=await keyboards.to_kbi())
        return
    if len(formatted) > 4000:
        await message.answer(await utils.host_text(format_exif_data(exif_data, False)))
    else:
        await message.answer(format_exif_data(exif_data))
