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
        wind_kph = current['wind_kph']

        # Only for forecast weather
        if weather_data.get('forecast') is not None:
            forecast = weather_data['forecast']
            forecast_day = forecast['forecastday'][0]["date"]

            weather_message = (
                f"🌡️<code>{temp_c}°C</code> {emoji} <code>{condition}</code> \n\n"
                f"<b>{city}, {country}</b>\n"
                f"{i18n.get("parsing-weather-forecast-day")}:  <b>{forecast_day}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
            )
            weather_message += _forecast_formatting_by_hours(forecast, i18n=i18n)


        else:
            weather_message = (
                f"<b>{i18n.get("parsing-weather-temperature")}:</b>   <code>{temp_c}°C</code>\n"
                f"<b>{i18n.get("parsing-weather-current")}:</b>  {emoji} <code>{condition}</code> \n\n"
                f"<b>{city}, {country}</b>\n"
                f"{i18n.get("parsing-weather-time")}:   <b>{local_time}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━"
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
            f"{i18n.get("parsing-weather-time")}:  <code>{hour_data["time"].split()[1]}</code>   🌡️ <code>{hour_data["temp_c"]}°C</code>\n"
            f"{emoji} <code>{hour_data["condition"]["text"]}</code> \n"
            f"-------------------------------\n"
        )
        res += weather_for_hour

    return res


def parse_time_zone(data: Dict[str, Any]) -> str:
    return data["location"]["tz_id"]
