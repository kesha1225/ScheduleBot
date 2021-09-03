import datetime
import re
from typing import List, Optional
from _types import WEEK_SCHEDULE, DAYS, DAY_SCHEDULE, LESSON
from storage import get_schedule_and_days
from utils import (
    get_now,
    get_start_end_datetime,
    get_start_end_timedelta,
    create_word_for_hour,
    create_word_for_minute,
    create_text_schedule_for_one_lesson,
    create_word_for_day,
    get_current_timedelta,
    create_text_schedule,
)


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
    now = get_now()
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

        # TODO: start_datetime почему то +2:30

        next_lesson_time = (
            start_datetime - now - datetime.timedelta(minutes=30)
        )  # 1 day, 15:53:00
        print(start_datetime)
        print(now)
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


def get_current_lesson(current_schedule: DAY_SCHEDULE) -> Optional[LESSON]:
    current_timedelta = get_current_timedelta()
    for lesson in current_schedule:
        start_timedelta, end_timedelta = get_start_end_timedelta(lesson)

        if start_timedelta <= current_timedelta <= end_timedelta:
            return lesson
    return None


async def create_one_day_schedule(date: datetime.datetime, tomorrow: bool = False):
    schedule, days = await get_schedule_and_days()
    for day in days:
        if int(day.split(".")[0]) == date.day:
            current_schedule = schedule[days.index(day)]
            text = "Завтра" if tomorrow else "Сегодня"
            response = f"{text} - {date.strftime('%d.%m.%Y')}\n{create_text_schedule(current_schedule)}"

            return response
