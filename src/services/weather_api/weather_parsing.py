import logging

from typing import Dict, Any
from fluentogram import TranslatorRunner

from src.services.weather_api.weather_emojis import get_weather_emoji

logger = logging.getLogger(__name__)


def parse_weather(weather_data: Dict[str, Any], i18n: TranslatorRunner) -> str:
    try:
        location = weather_data['location']
        current = weather_data['current']

        city = location['name']
        country = location['country']
        local_time = location['localtime']

        temp_c = current['temp_c']
        feels_like_c = current['feelslike_c']
        condition = current['condition']['text']
        emoji = get_weather_emoji(current['condition']['code'])
        humidity = current['humidity']
        wind_kph = current['wind_kph']

        # Only for forecast weather
        if weather_data.get('forecast') is not None:
            forecast = weather_data['forecast']
            forecast_day = forecast['forecastday'][0]["date"]

            weather_message = (
                f"<b>{city}, {country}</b>\n\n"
                f"<b>{i18n.get("parsing-weather-forecast-day")}:</b>  <code>{forecast_day}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            weather_message += _forecast_formatting_by_hours(forecast, i18n=i18n)


        else:
            weather_message = (
                f"<b>{city}, {country}</b>\n\n"
                f"<b>{i18n.get("parsing-weather-time")}:</b>   <code>{local_time}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>{i18n.get("parsing-weather-temperature")}:</b>   <code>{temp_c}°C</code>\n\n"
                f"<b>{i18n.get("parsing-weather-feels-like")}:</b>   <code>{feels_like_c}°C</code>\n"
                f"<b>{i18n.get("parsing-weather-current")}:</b>   <code>{condition}</code> {emoji}\n"
                f"<b>{i18n.get("parsing-weather-wind")}:</b>   <code>{wind_kph}km/h</code>\n\n"
            )

        return weather_message

    except Exception as e:
        logger.error(e)
        raise


def _forecast_formatting_by_hours(weather_data: Dict[str, Any], i18n: TranslatorRunner) -> str:
    res = ""

    # start from 08:00 with step 4 hours
    for hour_data in weather_data["forecastday"][0]["hour"][8::4]:
        emoji = get_weather_emoji(hour_data["condition"]["code"])

        weather_for_hour = (
            f"<b>{i18n.get("parsing-weather-time")}:</b> <code>{hour_data["time"].split()[1]}</code>\n"
            f"<b>{i18n.get("parsing-weather-temperature")}:</b> <code>{hour_data["temp_c"]}°C</code>\n"
            f"<b>{i18n.get("parsing-weather-feels-like")}:</b> <code>{hour_data["feelslike_c"]}°C</code>\n"
            f"<b>{i18n.get("parsing-weather-current")}:</b> <code>{hour_data["condition"]["text"]}</code> {emoji}\n"
            f"<b>{i18n.get("parsing-weather-wind")}:</b> <code>{hour_data["wind_kph"]}km/h</code>\n\n"
            f"-------------------------------\n"

        )
        res += weather_for_hour

    return res
