from aiogram_dialog.widgets.kbd import Cancel

from src.bot.dialogs.widgets.i18n import I18nFormat

MAIN_SETTINGS_BUTTON = Cancel(
    text=I18nFormat("back-button"),
    id="reply_back_button",
)
