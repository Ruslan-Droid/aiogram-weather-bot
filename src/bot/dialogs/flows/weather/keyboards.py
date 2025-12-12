from aiogram_dialog.widgets.kbd import Cancel, Button, ScrollingGroup
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs.widgets.i18n import I18nFormat

MAIN_SETTINGS_BUTTON = Cancel(
    text=I18nFormat("back-button"),
    id="reply_back_button",
)


def create_group_buttons_factory(groups_data: list[dict] = None):
    """Фабрика для создания кнопок групп"""
    if not groups_data:
        return ScrollingGroup(
            Button(Const("Нет групп"), id="no_groups"),
            id="groups",
            width=1,
            height=5,
        )

    # Создаем список кнопок
    buttons = []
    for group in groups_data:
        # Создаем текст для кнопки с эмодзи
        emoji = "👥"  # можно добавить логику для разных типов чатов

        # Используем Button с Format для динамического текста
        # Но нам нужно передать данные группы
        btn = Button(
            Const(f"{emoji} {group['title']}"),
            id=f"group_{group['id']}",  # уникальный id для каждой группы
            # Здесь нужен обработчик нажатия
        )
        buttons.append(btn)

    # Возвращаем ScrollingGroup с кнопками
    return ScrollingGroup(
        *buttons,  # распаковываем список кнопок
        id="groups",
        width=1,
        height=5,
    )