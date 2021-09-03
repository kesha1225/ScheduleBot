import datetime
import os
import json
import random
from typing import Tuple, Callable

from pytz import timezone
import pymorphy2

from _types import DAY_SCHEDULE, LESSON

morph = pymorphy2.MorphAnalyzer()


def create_word_for_hour(hour: int):
    return morph.parse("час")[0].make_agree_with_number(hour).word


def create_word_for_minute(minute: int):
    if minute == 1:
        return "минуту"
    return (
        morph.parse("минута")[0].make_agree_with_number(minute).inflect({"gent"}).word
    )


def create_word_for_day(day: int):
    return morph.parse("день")[0].make_agree_with_number(day).word


def create_text_schedule_for_one_lesson(lesson: LESSON) -> str:
    return (
        create_text_schedule([lesson])
        .replace("Пара №1:\n", "")
        .replace("--------------------", "")
    )


def create_text_schedule(schedule: DAY_SCHEDULE) -> str:
    response = ""
    old_times = []
    i = 1
    for subject in schedule:
        group_info = subject["group"] + "\n" if subject["group"] else ""

        previous_group_info = None
        if schedule.index(subject) != 0:
            previous_group_info = schedule[schedule.index(subject) - 1]["group"]
        if (
            group_info == "ИС-29 б\n"
            and previous_group_info == "ИС-29 а"
            and not subject["link"].strip()
            or subject["time"] in old_times
        ):
            continue
        response += f"Пара №{i}:\n{subject['time']}\n{subject['title']}\n"
        old_times.append(subject["time"])

        if subject["classroom"]:
            next_subject_time = None
            if schedule.index(subject) + 1 < len(schedule):
                next_subject_time = schedule[schedule.index(subject) + 1]["time"]

            if (
                group_info == "ИС-29 а\n" and (next_subject_time in old_times)
            ) and next_subject_time is not None:
                isb_classroom = schedule[schedule.index(subject) + 1]["classroom"]
                isb_teacher = schedule[schedule.index(subject) + 1]["teacher"]
                response += f"\nИС-29 а - {subject['classroom']} ({subject['teacher']})\nИС-29 б - {isb_classroom} ({isb_teacher})"
            elif group_info == "ИС-29 б\n" and previous_group_info != "ИС-29 а":
                response += f"\nИС-29 б - {subject['classroom']} ({subject['teacher']})"
            elif group_info == "ИС-29 а\n" and previous_group_info != "ИС-29 б":
                response += f"\nИС-29 а - {subject['classroom']} ({subject['teacher']})"
            else:
                response += f"\nИС-29 - {subject['classroom']} ({subject['teacher']})"
        if subject["link"].strip():
            response += f"\n{group_info} - {subject['link']}"
        if subject["note"]:
            response += f"\nПримечание - {subject['note']}"
        response += "\n--------------------\n"
        i += 1
    return response


def create_percent(user_id: int, now: datetime.datetime) -> int:
    random_data_file = os.path.dirname(__file__) + "/random_data.json"
    if not os.path.exists(random_data_file):
        with open(random_data_file, "w") as f:
            f.write(json.dumps({}))
    with open(random_data_file) as f:
        data: dict = json.loads(f.read())

    key = now.strftime("%d%m%Y") + str(user_id)
    if data.get(key) is not None:
        percent = data[key]
    else:
        percent = random.randint(0, 100)
        data[key] = percent
        with open(random_data_file, "w") as f:
            f.write(json.dumps(data))
    return percent


def get_now() -> datetime.datetime:
    nino_time = timezone("Europe/Moscow")
    return datetime.datetime.now(nino_time)


def get_current_timedelta() -> datetime.timedelta:
    now = get_now()
    current_hour, current_minute = now.strftime("%H:%M").split(":")
    return datetime.timedelta(hours=int(current_hour), minutes=int(current_minute))


def get_start_end_datetime(
    lesson: LESSON, schedule_year: int, schedule_month: int, schedule_day: int
) -> Tuple[datetime.datetime, datetime.datetime]:
    start_time, end_time = lesson["time"].split("–")
    start_hour, start_minute = start_time.split(":")
    start_datetime = datetime.datetime(
        year=schedule_year,
        month=schedule_month,
        day=schedule_day,
        hour=int(start_hour),
        minute=int(start_minute),
        tzinfo=timezone("Europe/Moscow"),
    )

    end_hour, end_minute = end_time.split(":")
    end_datetime = datetime.datetime(
        year=schedule_year,
        month=schedule_month,
        day=schedule_day,
        hour=int(end_hour),
        minute=int(end_minute),
        tzinfo=timezone("Europe/Moscow"),
    )

    return start_datetime, end_datetime


def get_start_end_timedelta(
    lesson: LESSON,
) -> Tuple[datetime.timedelta, datetime.timedelta]:
    start_time, end_time = lesson["time"].split("–")
    start_hour, start_minute = start_time.split(":")
    start_timedelta = datetime.timedelta(
        hours=int(start_hour),
        minutes=int(start_minute),
    )

    end_hour, end_minute = end_time.split(":")
    end_timedelta = datetime.timedelta(hours=int(end_hour), minutes=int(end_minute))

    return start_timedelta, end_timedelta


def format_day(raw_time: str, current_year: int):
    return raw_time.replace(f".{current_year}", "")


def is_weekend(now: datetime.datetime):
    return now.isoweekday() in (6, 7)
