import base64
import html
import inspect
import typing

import base58
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
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
        self.banned_methods = ('')

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
        return self.history if len(self.history) >= 1 else []

    def _list_methods_without_additional_args(self):
        """
        Return a list of all user-available Chepy methods with their signatures.
        """
        methods = []
        for name, member in inspect.getmembers(self, predicate=inspect.isroutine):
            # Skip private and internal methods
            if name.startswith('_'):
                continue
            # Get the signature, if possible
            try:
                sig = inspect.signature(member)
            except (ValueError, TypeError):
                sig = None
            # Format as name(signature)
            if len(sig.parameters.keys()) > 1 or name in self.banned_methods:
                continue
            methods.append(name)
        return sorted(methods)


class ChepyTool(StatesGroup):
    main = State()


def letter_methods(methods: list[str]):
    methods.sort()
    result = {}

    # Group methods by first letter
    letter_groups = {}
    for method in methods:
        first_letter = method[0]
        if first_letter not in letter_groups:
            letter_groups[first_letter] = []
        letter_groups[first_letter].append(method)

    current_key = ""
    current_methods = []

    for letter in sorted(letter_groups.keys()):
        methods_for_letter = letter_groups[letter]

        if len(methods_for_letter) > 20:
            for i in range(0, len(methods_for_letter), 20):
                chunk = methods_for_letter[i:i + 20]
                chunk_key = f"{letter}{i // 20 + 1}" if i > 0 else letter
                result[chunk_key] = chunk
        else:
            if current_methods and len(current_methods) + len(methods_for_letter) > 20:
                result[current_key] = current_methods
                current_key = letter
                current_methods = methods_for_letter
            else:
                if not current_key:
                    current_key = letter
                else:
                    current_key += letter
                current_methods.extend(methods_for_letter)

    # Add the last group if it exists
    if current_methods:
        result[current_key] = current_methods

    return result

def build_methods_keyboard(c, current_letter_group: str = None) -> InlineKeyboardMarkup:
    all_methods = c._list_methods_without_additional_args()
    kb = InlineKeyboardBuilder()

    letter_groups = letter_methods(all_methods)

    if current_letter_group and current_letter_group in letter_groups:
        methods = letter_groups[current_letter_group]

        for method in methods:
            kb.row(
                InlineKeyboardButton(
                    text=method,
                    callback_data=f"chepy:method:{method}"
                )
            )

    letter_buttons = []
    for letter_group in sorted(letter_groups.keys()):
        text = f"[{letter_group}]" if letter_group == current_letter_group else letter_group
        letter_buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=f"chepy:letter:{letter_group}"
            )
        )

        if len(letter_buttons) == 4:
            kb.row(*letter_buttons)
            letter_buttons = []

    if letter_buttons:
        kb.row(*letter_buttons)

    kb.row(keyboards.canceli(True))

    return kb.as_markup()



async def chepy_start_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text:
        msg = await message.answer('<b>Отправьте боту текст!</b>', reply_markup=keyboards.to_kbi())
        await state.update_data({'delete': [msg.message_id] if 'delete' not in data else [*data['delete'], msg.message_id]})
        return

    c = ChepyExtra(message.text)
    await state.update_data({'chepy': c})

    await message.answer(f"<code>{html.escape(str(message.text))}</code>\n"
                               "<b>Выберите действие:</b>", reply_markup=build_methods_keyboard(c))
    # await state.update_data({'remove_msg': msg})


async def chepy_callback_handler(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        c: ChepyExtra = data.get('chepy')

        # if not c:
        #     await call.answer("Сначала отправьте текст!")
        #     return

        action_parts = call.data.split(':')
        action_type = action_parts[1]

        if action_type == "letter":
            letter_group = action_parts[2]
            await call.message.edit_reply_markup(reply_markup=build_methods_keyboard(c, letter_group))
            await call.answer()
            return

        elif action_type == "method":
            method = action_parts[2]

            if method not in c._list_methods_without_additional_args():
                await call.answer("Метод не найден!")
                return

            result: ChepyExtra = getattr(c, method)()
            formatted_result = result.o

            if isinstance(formatted_result, dict):
                formatted_result = "\n".join(
                    f"<b>{html.escape(str(k))}</b>: <code>{html.escape(v.decode())}</code>" for k, v in
                    formatted_result.items())
            elif isinstance(formatted_result, bytes):
                formatted_result = f"<code>{html.escape(formatted_result.decode())}</code>"

            def make_history(hist: typing.Sequence[bytes]):
                text = "<code>"
                for h in hist:
                    if isinstance(h, dict):
                        h = b"<dict>"
                    text += f"{html.escape(h.decode())}</code>, <code>"
                text = text[:-8]
                return text

            await call.message.edit_text(
                f"{formatted_result}\n"
                f"История: {make_history(c.get_history)}",
                reply_markup=build_methods_keyboard(c)
            )
            await state.update_data({'chepy': result})

        elif action_type == "cancel":
            await state.clear()
            await call.message.edit_text("Операция отменена")

        await call.answer()

    except Exception as e:
        await call.answer(f"Произошла ошибка. Возможно, вы выбрали неверный метод.\n{e}")
        return