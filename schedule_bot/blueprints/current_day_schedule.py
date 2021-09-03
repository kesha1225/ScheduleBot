import json

from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    SimpleBotEvent,
    BaseEvent,
)
from vkwave.bots.core import BaseFilter
from vkwave.bots.core.dispatching.filters.base import FilterResult
from vkwave.bots.storage.types import Key

from helpers import get_schedule_and_days
from storage import storage
from utils import create_text_schedule

current_day_schedule_router = DefaultRouter()


class IsDayRequestMessage(BaseFilter):
    async def check(self, event: BaseEvent) -> FilterResult:
        return FilterResult(
            event.object.object.message.payload
            and json.loads(event.object.object.message.payload).get("day") is not None
        )


@simple_bot_message_handler(current_day_schedule_router, IsDayRequestMessage())
async def day_schedule(event: SimpleBotEvent):
    # TODO: слать инлайн клаву снова
    schedule, days = await get_schedule_and_days()

    day_data: str = json.loads(event.object.object.message.payload)["day"]

    current_schedule = schedule[days.index(day_data)]
    response = create_text_schedule(current_schedule)

    kb = await storage.get(Key("current_kb"))
    await event.answer(f"{day_data}\n{response}", dont_parse_links=True, keyboard=kb.get_keyboard())
