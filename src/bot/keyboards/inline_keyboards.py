from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluentogram import TranslatorRunner


def get_private_chat_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    url_to_private_chat = f"tg://resolve?domain=KLG_Weather_Bot"
    button = InlineKeyboardButton(text=i18n.get("button-with-bot-link"), url=url_to_private_chat)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard
