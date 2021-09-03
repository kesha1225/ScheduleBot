import re
import datetime
from typing import Tuple, List, Optional

import aiohttp
from bs4 import BeautifulSoup
from pytz import timezone

from _types import WEEK_SCHEDULE, DAYS
from utils import format_day

SCHEDULE_URL = (
    "http://spravka.nngasu.ru/schedule/schedule/student?"
    "user_bitrix_id=2437&param={bitrix_code}&ScheduleSearch%5Bstart_date%5D={start}"
    "&ScheduleSearch%5Bend_date%5D={end}&ScheduleSearch%5Bis_remote%5D="
)


SCHEDULE_RE = re.compile(
    r"https://spravka\.nngasu\.ru/schedule/schedule/student\?user_bitrix_id=2437&param=(.+)\" "
)


session = aiohttp.ClientSession()


async def get_bitrix_code() -> List[str]:
    async with session.post(
        "https://nngasu.ru/cdb/schedule/student.php?login=yes",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "referrer": "https://nngasu.ru/cdb/schedule/student.php?login=yes",
        },
        data="AUTH_FORM=Y&TYPE=AUTH&backurl=%2Fcdb%2Fschedule%2Fstudent.php&USER_LOGIN=gr_IS-29&USER_PASSWORD=916j9w&Login=%C2%EE%E9%F2%E8",
    ) as resp:
        text = await resp.text()
        return re.findall(SCHEDULE_RE, text)


def parse_schedule(schedule_html: str) -> Tuple[WEEK_SCHEDULE, DAYS]:
    soup = BeautifulSoup(schedule_html, "html.parser")
    main_table = soup.find("table")

    all_lessons = []
    days = []

    current_lessons = []
    for row in main_table.find_all("tr")[1:]:

        day_title = row.find(class_="day-title")
        if day_title is not None:
            days.append(day_title.get_text())
            if current_lessons:
                all_lessons.append(current_lessons)
                current_lessons = []
            continue

        time, title, group, teacher, classroom, link, note = map(
            lambda data: data.get_text()
            if data.find(class_="glyphicon glyphicon-new-window") is None
            else data.find(class_="glyphicon glyphicon-new-window").get("href"),
            row.find_all("td"),
        )
        lessons_data = {
            "time": time,
            "title": title,
            "group": group,
            "teacher": teacher,
            "classroom": classroom,
            "link": link,
            "note": note,
        }

        current_lessons.append(lessons_data)

    if current_lessons:
        all_lessons.append(current_lessons)

    return all_lessons, days


async def get_week_schedule() -> Optional[Tuple[WEEK_SCHEDULE, DAYS]]:
    nino_time = timezone("Europe/Moscow")
    now = datetime.datetime.now(nino_time)
    future = now + datetime.timedelta(days=7)
    bitrix_code = await get_bitrix_code()
    if not bitrix_code:
        return None

    async with session.get(
        SCHEDULE_URL.format(
            start=now.strftime("%d.%m.%Y"),
            end=future.strftime("%d.%m.%Y"),
            bitrix_code=bitrix_code[0],
        )
    ) as resp:
        text = await resp.text()
    return parse_schedule(text)
