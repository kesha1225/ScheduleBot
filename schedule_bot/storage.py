import asyncio
import logging
import traceback
from typing import Tuple

from vkwave.bots import TTLStorage

from vkwave.bots.storage.types import Key

from _types import WEEK_SCHEDULE, DAYS
from keyboard import create_current_kb
from schedule_parser import get_week_schedule

storage = TTLStorage(default_ttl=600)


async def get_schedule() -> WEEK_SCHEDULE:
    schedule = await storage.get(Key("current_schedule"))
    return schedule


async def get_days() -> DAYS:
    days = await storage.get(Key("current_days"))
    return days


async def get_schedule_and_days() -> Tuple[WEEK_SCHEDULE, DAYS]:
    schedule, days = await asyncio.gather(get_schedule(), get_days())
    return schedule, days


async def update_all() -> None:
    schedule, days = await get_week_schedule()
    await storage.put(key=Key("current_days"), value=days)
    await storage.put(key=Key("current_schedule"), value=schedule)
    await storage.put(
        key=Key("current_kb"), value=await create_current_kb(await get_days())
    )


async def update_all_forever():
    while True:
        try:
            await update_all()
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(traceback.format_exc())
            continue
