import datetime

from vkwave.bots import Keyboard, ButtonColor

from _types import DAYS
from utils import format_day


def get_default_kb() -> Keyboard:
    default_kb = Keyboard()
    default_kb.add_text_button(
        text="Расписание", color=ButtonColor.POSITIVE, payload={"command": "schedule"}
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какие сегодня пары?",
        color=ButtonColor.SECONDARY,
        payload={"command": "today"},
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какая сейчас пара?",
        color=ButtonColor.SECONDARY,
        payload={"command": "which"},
    )
    default_kb.add_text_button(
        text="Какая некст пара?",
        color=ButtonColor.SECONDARY,
        payload={"command": "next"},
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какие пары завтра?",
        color=ButtonColor.PRIMARY,
        payload={"command": "tomorrow"},
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Идти ли сегодня на пары?",
        color=ButtonColor.NEGATIVE,
        payload={"command": "go"},
    )
    return default_kb


async def create_current_kb(days: DAYS) -> Keyboard:
    kb = Keyboard(inline=True)
    year = datetime.datetime.now().year
    for i, day in enumerate(days, start=1):
        if i % 2 == 0:
            kb.add_row()
        kb.add_text_button(
            text=format_day(day, year),
            color=ButtonColor.SECONDARY,
            payload={"day": day},
        )
    return kb
