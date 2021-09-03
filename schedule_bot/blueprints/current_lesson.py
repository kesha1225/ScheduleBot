from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    PayloadFilter,
    SimpleBotEvent,
)

from helpers import get_current_schedule_for_which_and_next, get_current_lesson
from utils import create_text_schedule_for_one_lesson

current_lesson_router = DefaultRouter()


@simple_bot_message_handler(current_lesson_router, PayloadFilter({"command": "which"}))
async def send_schedule(event: SimpleBotEvent):
    current_schedule = await get_current_schedule_for_which_and_next()
    if current_schedule is None:
        return "Какие пары иди спи"

    current_lesson = get_current_lesson(current_schedule)
    if current_lesson is not None:
        return await event.answer(
            message=create_text_schedule_for_one_lesson(current_lesson),
            dont_parse_links=True,
        )

    return "Сейчас пары нет"
