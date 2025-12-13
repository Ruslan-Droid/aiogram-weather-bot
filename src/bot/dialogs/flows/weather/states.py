from aiogram.fsm.state import State, StatesGroup


class WeatherSG(StatesGroup):
    weather_main_menu = State()
    weather_general_settings = State()
    weather_changing_coords = State()
    weather_changing_time = State()
    weather_changing_city = State()
    weather_save_city = State()
    weather_group_settings = State()
    weather_edit_group = State()