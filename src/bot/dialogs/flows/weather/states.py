from aiogram.fsm.state import State, StatesGroup


class WeatherSG(StatesGroup):
    # main menu
    weather_main_menu = State()
    # Private settings
    weather_general_settings = State()
    weather_changing_coords = State()
    weather_changing_time = State()
    weather_changing_city = State()
    weather_save_city = State()
    # Group settings
    weather_group_settings = State()
    weather_edit_group = State()
    weather_edit_group_language = State()
    # to change tasks for groups
    weather_edit_group_task = State()  # Choosing task #1 or #2
    weather_group_task_settings = State()  # Edit chosen task
    weather_group_task_changing_time = State()
    weather_group_task_changing_city = State()
    weather_group_task_save_city = State()
    weather_group_task_changing_coords = State()
