from vkwave.bots import (
    DefaultRouter,
    simple_bot_message_handler,
    PayloadFilter,
    SimpleBotEvent,
)

from helpers import (
    get_current_schedule_for_which_and_next,
    get_current_lesson,
    get_schedule_and_days,
    create_next_lesson_message,
    correct_schedule,
)
from utils import get_now, get_current_timedelta

next_lesson_router = DefaultRouter()


@simple_bot_message_handler(next_lesson_router, PayloadFilter({"command": "next"}))
async def next_lesson(event: SimpleBotEvent):
    schedule, days = await get_schedule_and_days()
    now = get_now()
    current_schedule = await get_current_schedule_for_which_and_next()

    if current_schedule is None:
        return "некст пара не обнаружена))"
    current_timedelta = get_current_timedelta()
    current_lesson = get_current_lesson(current_schedule)

    message = create_next_lesson_message(
        current_schedule=current_schedule,
        current_timedelta=current_timedelta,
        current_lesson=current_lesson,
        days=days,
        all_schedule=schedule,
    )
    if message is None:
        # сейчас последняя пара, делаем на день вперед
        current_schedule = correct_schedule(
            days=days, schedule=schedule, today=now.day + 1
        )
        i = 1
        while current_schedule is None:
            current_schedule = correct_schedule(
                days=days, schedule=schedule, today=now.day + i
            )
            i += 1
        message = create_next_lesson_message(
            current_schedule=current_schedule,
            current_timedelta=current_timedelta,
            current_lesson=current_lesson,
            days=days,
            all_schedule=schedule,
        )

    return await event.answer(
        message=message,
        dont_parse_links=True,
    )
