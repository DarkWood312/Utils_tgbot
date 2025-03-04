import base64
import html

from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.types import Message
from cryptography.fernet import Fernet, InvalidToken


class Encryption:
    def __init__(self, key: str):
        if len(key) < 32:
            key = key + '@' * (32 - len(key))
        elif len(key) > 32:
            key = key[:32]
        self.key = key
        self.crypt = Fernet(base64.urlsafe_b64encode(self.key.encode()))

    def encrypt(self, to_encrypt: str):
        encrypted = self.crypt.encrypt(to_encrypt.encode())

        return encrypted.decode()

    def decrypt(self, encrypted: str):
        decrypted = self.crypt.decrypt(encrypted)

        return decrypted.decode()


async def encrypt_cmd(message: Message, command: CommandObject):
    await message.delete()
    if not command.args or len(command.args.split(' ', 1)) < 2:
        await message.answer(f'*Использование:* /{command.command} <ключ> <текст>', parse_mode=ParseMode.MARKDOWN)
        return
    args = command.args.split(' ', 1)
    key, to_encrypt = args

    enc = Encryption(key)
    encrypted = enc.encrypt(to_encrypt)
    await message.answer(f'<b>Зашифрованный текст:</b> <code>{html.escape(encrypted)}</code>\n\n'
                         f'<b>Ключ:</b> <tg-spoiler>{html.escape(key)}</tg-spoiler>')


async def decrypt_cmd(message: Message, command: CommandObject):
    await message.delete()
    if not command.args or len(command.args.split(' ', 1)) < 2:
        await message.answer(f'*Использование:* /{command.command} <ключ> <текст для расшифровки>', parse_mode=ParseMode.MARKDOWN)
        return
    args = command.args.split(' ', 1)
    key, to_decrypt = args

    enc = Encryption(key)
    try:
        encrypted = enc.decrypt(to_decrypt)
    except InvalidToken:
        await message.answer(f'<b>Неверный ключ!</b>')
        return
    await message.answer(f'<b>Расшифрованный текст:</b> <code>{html.escape(encrypted)}</code>')