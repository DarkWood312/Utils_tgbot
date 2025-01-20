from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext


class AnyStateFilter(BaseFilter):
    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        return True