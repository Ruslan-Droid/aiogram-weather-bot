from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import ScrollingGroup, Button
from aiogram_dialog.widgets.text import Const


class GroupsScrollingGroup(ScrollingGroup):
    def __init__(
            self,
            id: str,
            data_key: str = "groups_data",
            on_click=None,
            width: int = 1,
            height: int = 5,
            when: WhenCondition = None,
    ):
        self.data_key = data_key
        self.on_click_handler = on_click
        super().__init__(*[], id=id, width=width, height=height, when=when)

    async def _render_keyboard(self, data, manager):
        # Получаем данные из геттера
        groups_data = data.get(self.data_key, [])

        # Создаем кнопки
        buttons = []
        for group in groups_data:
            btn = Button(
                Const(group.get("title", f"Группа {group.get('group_telegram_id')}")),
                id=f"group_{group.get('group_telegram_id')}",
                on_click=self.on_click_handler,
            )
            buttons.append(btn)

        if not buttons:
            buttons.append(Button(Const("🚫 Нет групп"), id="no_groups"))

        # Обновляем кнопки
        self.buttons = buttons


        return await super()._render_keyboard(data, manager)