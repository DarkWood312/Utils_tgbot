import logging
from multiprocessing.forkserver import read_signed
from typing import *

from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import Update, Message
from pyexpat.errors import messages


async def LoggingMiddleware(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]) -> Any:
    user = data['event_from_user']
    if event.text:
        logging.info(f"User {user.id} ({user.full_name}) sent a message: {event.text}")
    return await handler(event, data)


async def SplitMessageMiddleware(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]) -> Any:
    # if event.message and event.message.text:
    #
    #     max_length = 1000
    #     print(event.message.text or 0, len(event.message.text or ''))
    #     if len(event.message.text) > max_length:
    #         chunks = [event.message.text[i:i + max_length] for i in range(0, len(event.message.text), max_length)]
    #         for chunk in chunks:
    #             print(len(chunk))
    #             await event.message.answer(chunk)
    #         raise CancelHandler()
    result: Message = await handler(event, data)
    print(result)
    return result


def register_middlewares(dp: Dispatcher):
    dp.message.outer_middleware.register(LoggingMiddleware)
    # dp.message.middleware.register(SplitMessageMiddleware)
