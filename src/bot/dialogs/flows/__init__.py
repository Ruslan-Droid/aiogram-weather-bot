from .registration.dialogs import registration_dialog
from .language_settings.dialogs import settings_dialog
from .weather.dialogs import weather_dialog

__all__ = ["dialogs"]

dialogs = [
    registration_dialog,
    settings_dialog,
    weather_dialog,
]
