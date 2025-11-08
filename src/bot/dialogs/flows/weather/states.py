from aiogram.fsm.state import State, StatesGroup


class WeatherSG(StatesGroup):
    weather_main_menu = State()
    weather_general_settings = State()
