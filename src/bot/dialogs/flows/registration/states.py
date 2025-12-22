from aiogram.fsm.state import State, StatesGroup


class StartRegistrationSG(StatesGroup):
    start_registration = State()
    send_city_registration = State()
    save_city_registration = State()
