from vkwave.bots import Keyboard, ButtonColor


def get_default_kb() -> Keyboard:
    default_kb = Keyboard()
    default_kb.add_text_button(
        text="Расписание", color=ButtonColor.POSITIVE, payload={"command": "schedule"}
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какая сейчас пара?",
        color=ButtonColor.NEGATIVE,
        payload={"command": "which"},
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Какая некст пара?",
        color=ButtonColor.PRIMARY,
        payload={"command": "next"},
    )
    default_kb.add_row()
    default_kb.add_text_button(
        text="Идти ли сегодня на пары?",
        color=ButtonColor.SECONDARY,
        payload={"command": "go"},
    )
    return default_kb
