from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    SimpleBotEvent,
    PayloadFilter,
)

from utils import get_now, create_percent, is_weekend

attend_apparently_router = DefaultRouter()


@simple_bot_message_handler(attend_apparently_router, PayloadFilter({"command": "go"}))
async def send_go(event: SimpleBotEvent):
    now = get_now()
    if is_weekend(now):
        return "В выходные поучиться захотелось?"

    percent = create_percent(user_id=event.object.object.message.from_id, now=now)

    await event.answer(f"Идти на пары стоит с вероятностью {percent}%")
