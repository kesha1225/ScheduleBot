import datetime

from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    SimpleBotEvent,
    PayloadFilter,
)

from helpers import create_one_day_schedule
from utils import get_now, is_weekend

tomorrow_schedule_router = DefaultRouter()


@simple_bot_message_handler(
    tomorrow_schedule_router, PayloadFilter({"command": "tomorrow"})
)
async def tomorrow(event: SimpleBotEvent):
    now = get_now()
    tomorrow_date = now + datetime.timedelta(days=1)
    if is_weekend(tomorrow_date):
        return "завтра выходной, хд"

    await event.answer(
        await create_one_day_schedule(tomorrow_date, tomorrow=True),
        dont_parse_links=True,
    )
