from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from fluentogram import TranslatorRunner


def request_coords_kb(i18n: TranslatorRunner) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=i18n.keyboard.coords(), request_location=True,
                )
            ],
        ],
        resize_keyboard=True,
    )
