import asyncio
import datetime
import json
import logging
import os
import re
import traceback
from typing import Tuple, Optional, List

from vkwave.bots import SimpleLongPollBot, Keyboard, ButtonColor, TTLStorage
from vkwave.bots.storage.types import Key
from dotenv import load_dotenv

from ._types import WEEK_SCHEDULE, DAYS, DAY_SCHEDULE, LESSON
from .keyboards import get_default_kb
from .schedule_parser import get_week_schedule
from .utils import (
    create_text_schedule,
    create_percent,
    create_word_for_hour,
    create_word_for_minute,
    create_text_schedule_for_one_lesson,
    get_now,
    get_current_timedelta,
    get_start_end_timedelta,
    create_word_for_day,
    get_start_end_datetime,
)

load_dotenv()

logging.basicConfig(filename="schedule_parser.log", level=logging.ERROR)

storage = TTLStorage(default_ttl=600)

bot = SimpleLongPollBot(
    os.getenv("TOKEN"),
    group_id=198546018,
)


async def get_schedule() -> WEEK_SCHEDULE:
    schedule = await storage.get(Key("current_schedule"))
    return schedule


async def get_days() -> DAYS:
    days = await storage.get(Key("current_days"))
    return days


async def get_schedule_and_days() -> Tuple[WEEK_SCHEDULE, DAYS]:
    schedule, days = await asyncio.gather(get_schedule(), get_days())
    return schedule, days


def correct_schedule(
    days: List[str], schedule: WEEK_SCHEDULE, today: int
) -> Optional[DAY_SCHEDULE]:
    current_schedule = None
    for day in days:
        check_day = int(day.split(".")[0])
        if check_day == today:
            current_schedule = schedule[days.index(day)]
    return current_schedule


async def get_current_schedule_for_which_and_next() -> Optional[DAY_SCHEDULE]:
    schedule, days = await get_schedule_and_days()
    now = get_now()

    current_schedule = correct_schedule(days=days, schedule=schedule, today=now.day)

    # типа если сейчас уже все пары прошли то будет сегодняшние показывать без этого ужаса

    if (
        current_schedule is not None
        and int(current_schedule[-1]["time"].split(":")[0]) < now.hour
    ):
        # хз нужно ли это, в воскр все падает в штуку ниже и сюда не попадает тк в current_schedule None
        if now.isoweekday() + 1 == 6:
            current_schedule = correct_schedule(
                days=days, schedule=schedule, today=now.day + 3
            )
        elif now.isoweekday() + 1 == 7:
            current_schedule = correct_schedule(
                days=days, schedule=schedule, today=now.day + 2
            )
        else:
            current_schedule = correct_schedule(
                days=days, schedule=schedule, today=now.day + 1
            )

    # вдруг там нет пар или еще что, короче на всякий
    i = 1
    while current_schedule is None:
        current_schedule = correct_schedule(
            days=days, schedule=schedule, today=now.day + i
        )
        i += 1

    return current_schedule


@bot.message_handler(bot.payload_filter({"command": "schedule"}))
async def send_schedule(event: bot.SimpleBotEvent):
    kb = await storage.get(Key("current_kb"))
    await event.answer(keyboard=kb.get_keyboard(), message="Выберите день")


def get_current_lesson(current_schedule: DAY_SCHEDULE) -> Optional[LESSON]:
    current_timedelta = get_current_timedelta()
    for lesson in current_schedule:
        start_timedelta, end_timedelta = get_start_end_timedelta(lesson)

        if start_timedelta <= current_timedelta <= end_timedelta:
            return lesson
    return None


@bot.message_handler(bot.payload_filter({"command": "which"}))
async def send_schedule(event: bot.SimpleBotEvent):
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


def create_next_lesson_message(
    current_schedule: DAY_SCHEDULE,
    current_timedelta: datetime.timedelta,
    current_lesson: Optional[LESSON],
    all_schedule: WEEK_SCHEDULE,
    days: DAYS,
):
    schedule_date_str = days[all_schedule.index(current_schedule)].split(".")
    schedule_day = int(schedule_date_str[0])
    schedule_month = int(schedule_date_str[1])
    schedule_year = int(schedule_date_str[2].split("-")[0])
    now = datetime.datetime.now()
    for lesson in current_schedule:
        start_datetime, end_datetime = get_start_end_datetime(
            lesson,
            schedule_month=schedule_month,
            schedule_day=schedule_day,
            schedule_year=schedule_year,
        )
        start_timedelta, end_timedelta = get_start_end_timedelta(lesson)
        if (
            current_lesson is not None
            and current_schedule.index(lesson) <= current_schedule.index(current_lesson)
        ) or (end_timedelta < current_timedelta and schedule_day == now.day):
            continue

        next_lesson_time = start_datetime - now  # 1 day, 15:53:00
        days_left = re.findall(r"[-]?(\d+) day[s]?,", str(next_lesson_time))

        next_lesson_time_list = list(
            map(int, str(next_lesson_time).split()[-1].split(".")[0].split(":"))
        )
        hour_word = create_word_for_hour(next_lesson_time_list[0])
        minute_word = create_word_for_minute(next_lesson_time_list[1])
        next_lesson_text = create_text_schedule_for_one_lesson(lesson)

        day = 0
        if days_left:
            day = int(days_left[0])

        if day >= 1:
            day_word = create_word_for_day(day)
            message = (
                f"Следующая пара через {day} {day_word} {next_lesson_time_list[0]}"
                f" {hour_word} {next_lesson_time_list[1]} {minute_word}:\n\n{next_lesson_text}"
            )
        elif next_lesson_time_list[0] > 0:
            message = (
                f"Следующая пара через {next_lesson_time_list[0]}"
                f" {hour_word} {next_lesson_time_list[1]} {minute_word}:\n\n{next_lesson_text}"
            )
        else:
            message = f"Следующая пара через {next_lesson_time_list[1]} {minute_word}:\n\n{next_lesson_text}"
        return message
    return None


@bot.message_handler(bot.payload_filter({"command": "next"}))
async def next_lesson(event: bot.SimpleBotEvent):
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
    if message is not None:
        return await event.answer(
            message=message,
            dont_parse_links=True,
        )

    # сейчас последняя пара, делаем на день вперед
    current_schedule = correct_schedule(days=days, schedule=schedule, today=now.day + 1)

    # TODO: Тут тоже повтор, вынести куда то, а то спать хочу в падлу
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
    if now.isoweekday() in (6, 7):
        return "В выходные поучиться захотелось?"

    percent = create_percent(user_id=event.object.object.message.from_id, now=now)

    await event.answer(f"Идти на пары стоит с вероятностью {percent}%")


@bot.message_handler(bot.payload_filter({"command": "tomorrow"}))
async def tomorrow(event: bot.SimpleBotEvent):
    now = get_now()
    if now.isoweekday() in (5, 6):
        return "завтра выходной, хд"

    schedule, days = await get_schedule_and_days()
    tomorrow_date = now + datetime.timedelta(days=1)

    for day in days:
        # TODO: тут повтор, надо вынести куда то
        if int(day.split(".")[0]) == tomorrow_date.day:
            current_schedule = schedule[days.index(day)]
            response = f"Завтра - {tomorrow_date.strftime('%d.%m.%Y')}\n{create_text_schedule(current_schedule)}"

            await event.answer(response, dont_parse_links=True)


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
