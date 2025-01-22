import logging
from typing import *

from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types import Update
from pyexpat.errors import messages


async def LoggingMiddleware(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]) -> Any:
    user = data['event_from_user']
    if event.message and event.message.text:
        logging.info(f"User {user.id} ({user.full_name}) sent a message: {event.message.text}")
    return await handler(event, data)

async def SplitMessageMiddleware(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]) -> Any:
    print(data)
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
    return await handler(event, data)

def register_middlewares(dp: Dispatcher):
    dp.update.outer_middleware.register(LoggingMiddleware)
    # dp.update.middleware.register(SplitMessageMiddleware)
    # dp.update.outer_middleware.register(SplitMessageMiddleware)
