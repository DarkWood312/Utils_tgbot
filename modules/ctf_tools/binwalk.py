import os.path

import binwalkpy
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from extra import keyboards, utils
from extra.constants import bot


class Binwalk(StatesGroup):
    wait_for_file = State()

async def binwalk_handler(message: Message, state: FSMContext):
    # await bot.send_chat_action(message.chat.id, action='typing')
    data = await state.get_data()
    if message.photo:
        msg = await message.answer('<b>Отправьте боту файл!</b>', reply_markup=await keyboards.to_kbi())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return
    if not message.document:
        msg = await message.answer('<b>Это не файл!</b>', reply_markup=await keyboards.to_kbi())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return
    # await message.answer('Идет анализ файла...')
    if not os.path.exists('cache'):
        os.mkdir('cache')
    await bot.download(message.document.file_id, destination=f'cache/{message.from_user.id}.bin')
    scan_results = binwalkpy.scan_file(f"cache/{message.from_user.id}.bin")
    result_lines = []
    for item in scan_results:
        result_lines.append(f"<b>Description</b>: <code>{item['description']}</code>")
        result_lines.append(f"<b>Offset</b>: <code>{item['offset']}</code>")
        result_lines.append(f"<b>Size</b>: <code>{item['size']}</code> bytes")
        result_lines.append(f"<b>Confidence</b>: <code>{item['confidence']}</code>")
        result_lines.append("")

    if result_lines:
        await message.answer("\n".join(result_lines), reply_markup=await keyboards.canceli())
    else:
        await message.answer("Анализ не выявил известных сигнатур в файле.", reply_markup=await keyboards.canceli())
    os.remove(f'cache/{message.from_user.id}.bin')