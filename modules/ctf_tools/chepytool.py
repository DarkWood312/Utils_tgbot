import base64
import html
import inspect
import typing

import base58
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from chepy import Chepy
from chepy.core import ChepyDecorators

from extra import keyboards


class ChepyExtra(Chepy):
    def __init__(self, *initial_states):
        self._recording_enabled = False
        super().__init__(*initial_states)
        self.prev = None
        self.history = []
        self._recording_enabled = True

        #TODO
        self.available_methods = ('to_hex', 'from_hex', 'bruteforce_from_base_xx', 'bruteforce_to_base_xx', 'to_binary', 'from_binary',)

    def _record_state(self):
        """
        Internal: capture the current state into history and prev.
        """
        try:
            current = self.o
        except Exception:
            return
        if not self.history or self.history[-1] != current:
            self.history.append(current)
            self.prev = current

    def __getattribute__(self, name):
        """
        Intercept user-invoked Chepy operations to record state only once per call.
        """
        attr = super().__getattribute__(name)
        if callable(attr) and getattr(self, '_recording_enabled', False):
            skip = {'_record_state', '__init__', '__getattribute__', 'prev', 'history', 'o', 'out', '_recording_enabled'}
            if name not in skip:
                def wrapper(*args, **kwargs):
                    self._record_state()
                    self._recording_enabled = False
                    try:
                        return attr(*args, **kwargs)
                    finally:
                        self._recording_enabled = True
                return wrapper
        return attr

    @ChepyDecorators.call_stack
    def bruteforce_to_base_xx(self):
        """Try to encode the data with various base encoding methods

        Returns:
            Chepy: The Chepy object.
        """
        hold = {}
        data = self._convert_to_bytes()
        ops = {
            "base85": base64.a85encode,
            "base16": base64.b16encode,
            "base32": base64.b32encode,
            "base64": base64.b64encode,
            "base58": base58.b58encode,
        }

        for name, op in ops.items():
            try:
                result = op(data)
                hold[name] = result
            except Exception as e:
                hold[{name}] = None

        self.state = hold
        return self

    @property
    def get_history(self):
        return self.history[:-1] if len(self.history) > 1 else []

    # def list_methods(self):
    #     """
    #     Return a list of all user-available Chepy methods with their signatures.
    #     """
    #     methods = []
    #     for name, member in inspect.getmembers(Chepy, predicate=inspect.isroutine):
    #         # Skip private and internal methods
    #         if name.startswith('_'):
    #             continue
    #         # Get the signature, if possible
    #         try:
    #             sig = inspect.signature(member)
    #         except (ValueError, TypeError):
    #             sig = None
    #         # Format as name(signature)
    #         methods.append(f"{name}{sig}")
    #     return sorted(methods)


class ChepyTool(StatesGroup):
    main = State()


async def chepy_start_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text:
        msg = await message.answer('<b>Отправьте боту текст!</b>', reply_markup=await keyboards.to_kbi())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return

    c = ChepyExtra(message.text)
    await state.update_data({'chepy': c})
    reply_markup = InlineKeyboardBuilder()
    for method in c.available_methods:
        reply_markup.row(InlineKeyboardButton(text=method, callback_data=f'chepy:{method}'))
    reply_markup.row(await keyboards.canceli(True))

    await message.answer(f"<code>{html.escape(str(message.text))}</code>\n"
                               "<b>Выберите действие:</b>", reply_markup=reply_markup.as_markup())
    # await state.update_data({'remove_msg': msg})

async def chepy_callback_handler(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        c: ChepyExtra = data.get('chepy')
        # if not c:
        #     await call.answer("Сначала отправьте текст!")
        #     return
        method = call.data.split(':')[1]
        # if method not in c.available_methods:
        #     await call.answer("Метод не найден!")
        #     return
        result: ChepyExtra = getattr(c, method)()
        formatted_result = result.o


        if isinstance(formatted_result, dict):
            formatted_result = "\n".join(f"<b>{html.escape(str(k))}</b>: <code>{html.escape(v.decode())}</code>" for k, v in formatted_result.items())
        elif isinstance(formatted_result, bytes):
            formatted_result = f"<code>{html.escape(formatted_result.decode())}</code>"

        reply_markup = InlineKeyboardBuilder()
        for method in c.available_methods:
            reply_markup.row(InlineKeyboardButton(text=method, callback_data=f'chepy:{method}'))
        reply_markup.row(await keyboards.canceli(True))

        def make_history(hist: typing.Sequence[bytes]):
            # if isinstance(hist, dict):
            #     return f"<code>{html.escape("<dict>")}</code>"
            text = "<code>"
            for h in hist:
                if isinstance(h, dict):
                    h = b"<dict>"
                text += f"{html.escape(h.decode())}</code>, <code>"
            text = text[:-8]
            return text


        await call.message.edit_text(f"{formatted_result}\n"
                                  f"История: {make_history(c.get_history)}", reply_markup=reply_markup.as_markup())
        await state.update_data({'chepy': result})
        # if 'remove_msg' in data and data['remove_msg']:
        #     await data['remove_msg'].delete()

        await call.answer()
    except ConnectionAbortedError as e:
        await call.answer("Произошла ошибка. Возможно, вы выбрали неверный метод.")
        return