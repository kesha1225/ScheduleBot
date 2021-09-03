from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    PayloadFilter,
    SimpleBotEvent,
)
from vkwave.bots.storage.types import Key

from storage import storage

schedule_router = DefaultRouter()


@simple_bot_message_handler(schedule_router, PayloadFilter({"command": "schedule"}))
async def send_schedule(event: SimpleBotEvent):
    kb = await storage.get(Key("current_kb"))
    await event.answer(keyboard=kb.get_keyboard(), message="Выберите день")
