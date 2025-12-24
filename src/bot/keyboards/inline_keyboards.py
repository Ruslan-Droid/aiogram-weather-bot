from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluentogram import TranslatorRunner


def get_private_chat_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    url_to_private_chat = "tg://resolve?domain=KLG_Weather_Bot"
    button = InlineKeyboardButton(text=i18n.get("button-with-bot-link"), url=url_to_private_chat)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard


def get_help_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    url_to_support = "tg://resolve?domain=DarkGrayCaesar"
    url_to_git_hub = "https://github.com/Ruslan-Droid/aiogram-weather-bot"

    button_support = InlineKeyboardButton(text=i18n.get("support-button"), url=url_to_support)
    button_github = InlineKeyboardButton(text=i18n.get("github-button"), url=url_to_git_hub)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_support], [button_github]])

    return keyboard
