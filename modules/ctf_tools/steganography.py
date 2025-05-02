from io import BytesIO

import cv2
import numpy as np
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InputMediaPhoto, BufferedInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from extra.constants import bot

from extra import keyboards

class Steganography(StatesGroup):
    wait_for_file = State()


def analyze_image(img: bytes, ext: str = 'png', jpeg_quality: int = 95) -> dict[str, list[bytes]]:
    params = []
    if ext in ('jpg', 'jpeg'):
        params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
    ext = f'.{ext}'


    img = cv2.imdecode(np.frombuffer(img, dtype=np.uint8), cv2.IMREAD_COLOR)
    b, g, r = cv2.split(img)
    bit_channels = {}
    for channel, channel_img in (('b', b), ('g', g), ('r', r)):
        l = []
        for bit in range(8):
            b = (channel_img & (1 << bit)) >> bit
            bit_vis = (b * 255).astype(np.uint8)

            buf = cv2.imencode(ext, bit_vis, params)[1]
            l.append(buf.tobytes())
        bit_channels[channel] = l
    return bit_channels


async def steganography_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.document:
        msg = await message.answer('<b>Отправьте боту фото как файл!</b>', reply_markup=await keyboards.to_kbi())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return
    img = BytesIO()
    await bot.download(message.document, img)
    img.seek(0)
    analyzed = analyze_image(img.read())
    media_groups = []
    for channel, l in analyzed.items():
        media_group = MediaGroupBuilder()
        for bit, img in enumerate(l):
            media_group.add_photo(BufferedInputFile(img, filename=f"{channel.upper()}_{bit}.png"), caption=f'{channel.upper()}_{bit}.png')
        media_groups.append(media_group)
    for media_group in media_groups:
        await message.answer_media_group(media_group.build())
    await message.answer("Готово.", reply_markup=await keyboards.to_kbi())