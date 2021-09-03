import asyncio
import logging
import os

from vkwave.bots import SimpleLongPollBot
from dotenv import load_dotenv

from storage import update_all_forever

from blueprints import (
    attend_apparently_router,
    current_day_schedule_router,
    current_lesson_router,
    default_router,
    next_lesson_router,
    schedule_router,
    today_schedule_router,
    tomorrow_schedule_router,
)

load_dotenv()

# logging.basicConfig(filename="schedule_parser.log", level=logging.ERROR)

bot = SimpleLongPollBot(
    os.getenv("TOKEN"),
    group_id=int(os.getenv("GROUP_ID")),
)

bot.dispatcher.add_router(attend_apparently_router)
bot.dispatcher.add_router(current_day_schedule_router)
bot.dispatcher.add_router(current_lesson_router)
bot.dispatcher.add_router(next_lesson_router)
bot.dispatcher.add_router(schedule_router)
bot.dispatcher.add_router(today_schedule_router)
bot.dispatcher.add_router(tomorrow_schedule_router)
bot.dispatcher.add_router(default_router)


def run():
    loop = asyncio.get_event_loop()
    loop.create_task(update_all_forever())
    loop.create_task(bot.run(ignore_errors=True))
    loop.run_forever()
