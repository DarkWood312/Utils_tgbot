import logging
from typing import *

from aiogram import Dispatcher
from aiogram.types import Update


async def LoggingMiddleware(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]) -> Any:
    user = data['event_from_user']
    if event.message and event.message.text:
        logging.info(f"User {user.id} ({user.full_name}) sent a message: {event.message.text}")
    return await handler(event, data)


def register_middlewares(dp: Dispatcher):
    dp.update.middleware.register(LoggingMiddleware)
