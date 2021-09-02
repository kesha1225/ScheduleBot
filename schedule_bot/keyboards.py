from vkwave.bots import Keyboard, ButtonColor


def get_default_kb() -> Keyboard:
    default_kb = Keyboard()
    default_kb.add_text_button(
        text="Расписание", color=ButtonColor.POSITIVE, payload={"command": "schedule"}
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какаие сегодня пары?",
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
