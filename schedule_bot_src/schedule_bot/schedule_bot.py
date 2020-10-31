import asyncio
import traceback

import datetime
import logging
import json
from typing import Tuple

from pytz import timezone

from vkwave.bots import SimpleLongPollBot, Keyboard, ButtonColor, TTLStorage
from vkwave.bots.storage.types import Key

from .keyboards import get_default_kb
from .schedule_parser import get_week_schedule
from .utils import create_text_schedule, create_percent
from ._types import SCHEDULE, DAYS

logging.basicConfig(filename="schedule_parser.log", level=logging.ERROR)

storage = TTLStorage(default_ttl=600)

bot = SimpleLongPollBot(
    "7bee13626c43db9ebba1ba78d6646c1e614b92494e4b870706a2f2ed006b843a3b84f59e33d72447a3a54",
    group_id=198546018,
)


async def get_schedule() -> SCHEDULE:
    schedule = await storage.get(Key("current_schedule"))
    return schedule


async def get_days() -> DAYS:
    days = await storage.get(Key("current_days"))
    return days


async def get_schedule_and_days() -> Tuple[SCHEDULE, DAYS]:
    schedule, days = await asyncio.gather(get_schedule(), get_days())
    return schedule, days


def get_now() -> datetime.datetime:
    nino_time = timezone("Europe/Moscow")
    return datetime.datetime.now(nino_time)


@bot.message_handler(bot.payload_filter({"command": "schedule"}))
async def send_schedule(event: bot.SimpleBotEvent):
    kb = await storage.get(Key("current_kb"))
    await event.answer(keyboard=kb.get_keyboard(), message="Выберите день")


@bot.message_handler(bot.payload_filter({"command": "which"}))
async def send_schedule(event: bot.SimpleBotEvent):
    # TODO: доделать
    schedule, days = await get_schedule_and_days()
    now = get_now()
    current_schedule = None
    for day in days:
        if day.startswith(str(now.day)):
            current_schedule = schedule[days.index(day)]
    if current_schedule is None:
        return "Какие пары иди спи"
    for lesson in current_schedule:
        print(now.strftime("%H:%M"), lesson["time"])
        if now.strftime("%H:%M") in lesson["time"]:
            print(lesson)
    return "Пока не готово"


@bot.message_handler(
    lambda event: event.object.object.message.payload
    and json.loads(event.object.object.message.payload).get("day") is not None
)
async def day_schedule(event: bot.SimpleBotEvent):
    schedule, days = await get_schedule_and_days()

    day_data: str = json.loads(event.object.object.message.payload)["day"]

    current_schedule = schedule[days.index(day_data)]
    response = create_text_schedule(current_schedule)

    await event.answer(response, dont_parse_links=True)


@bot.message_handler(bot.payload_filter({"command": "go"}))
async def send_go(event: bot.SimpleBotEvent):
    now = get_now()
    if now.isoweekday() in (3, 6, 7):
        return "В выходные поучиться захотелось?"

    percent = create_percent(user_id=event.object.object.message.from_id, now=now)

    await event.answer(f"Идти на пары стоит с вероятностью {percent}%")


@bot.message_handler()
async def default(event: bot.SimpleBotEvent):
    await event.answer(
        keyboard=get_default_kb().get_keyboard(), message="Жмите кнопочки"
    )


async def create_current_kb() -> Keyboard:
    kb = Keyboard()
    for day in await get_days():
        kb.add_text_button(text=day, color=ButtonColor.SECONDARY, payload={"day": day})
        kb.add_row()
    kb.add_text_button("Назад", color=ButtonColor.NEGATIVE, payload={"command": "menu"})
    return kb


async def update_all() -> None:
    schedule, days = await get_week_schedule()
    await storage.put(key=Key("current_days"), value=days)
    await storage.put(key=Key("current_schedule"), value=schedule)
    await storage.put(key=Key("current_kb"), value=await create_current_kb())


async def update_all_forever():
    while True:
        try:
            await update_all()
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(traceback.format_exc())
            continue


def run():
    loop = asyncio.get_event_loop()
    loop.create_task(update_all_forever())
    loop.create_task(bot.run(ignore_errors=True))
    loop.run_forever()
