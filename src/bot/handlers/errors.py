import logging

from aiogram_dialog import DialogManager, ShowMode, StartMode

from src.bot.dialogs.flows.weather.states import WeatherSG

logger = logging.getLogger(__name__)


async def on_unknown_intent(event, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        WeatherSG.weather_main_menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    # Example of handling UnknownState Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        WeatherSG.weather_main_menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
