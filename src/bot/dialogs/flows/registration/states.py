from aiogram.fsm.state import State, StatesGroup


class StartRegistrationSG(StatesGroup):
    start_registration = State()
