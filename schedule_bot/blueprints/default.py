from vkwave.bots import DefaultRouter, simple_bot_message_handler, SimpleBotEvent

from keyboard import get_default_kb

default_router = DefaultRouter()


@simple_bot_message_handler(default_router)
async def default(event: SimpleBotEvent):
    await event.answer(
        keyboard=get_default_kb().get_keyboard(), message="Жмите кнопочки"
    )
