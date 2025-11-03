from pathlib import Path

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format

from src.bot.dialogs.flows.start_registration.getters import get_hello
from src.bot.dialogs.flows.start_registration.states import StartSG

animation_path = Path(__file__).parent / "media" / "test.gif"

start_dialog = Dialog(
    Window(
        Format("{hello}"),
        getter=get_hello,
        state=StartSG.start,
    ),
)
