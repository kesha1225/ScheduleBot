from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    SimpleBotEvent,
    PayloadFilter,
)

from helpers import create_one_day_schedule
from utils import get_now, is_weekend

today_schedule_router = DefaultRouter()


@simple_bot_message_handler(today_schedule_router, PayloadFilter({"command": "today"}))
async def today(event: SimpleBotEvent):
    now = get_now()
    if is_weekend(now):
        return "ниче нет"

    await event.answer(await create_one_day_schedule(now), dont_parse_links=True)
