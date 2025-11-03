from aiogram.fsm.state import State, StatesGroup


class WeatherSG(StatesGroup):
    weather = State()
