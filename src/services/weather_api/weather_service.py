import asyncio
import logging
import aiohttp
from urllib.parse import urljoin
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @staticmethod
    def _check_location_is_city_or_coords(value: str | tuple[float, float]) -> str:
        if type(value) is tuple:
            return f"{value[0]},{value[1]}"
        else:
            return value

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
           retry=retry_if_exception_type(aiohttp.ClientConnectionError))
    async def get_current_weather(
            self,
            location: str | tuple[float, float],
            language: str = "ru",
    ) -> Dict[str, Any]:

        q = self._check_location_is_city_or_coords(location)
        params = {
            "key": self.api_key,
            "q": q,
            "lang": language,
        }
        endpoint = "current.json"
        url = urljoin(self.base_url, endpoint)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(url=url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    data = await response.json()
                    logger.info("Successful get current weather with: %s", q)
                    return data
            except aiohttp.ClientConnectionError as e:
                logger.error("Connection error: %s", e)
                raise
            except aiohttp.ClientError as e:
                logger.error("Network error: %s", e)
                raise
            except asyncio.TimeoutError:
                logger.error("Timeout requesting weather for location: %s", q)
                raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
           retry=retry_if_exception_type(aiohttp.ClientConnectionError))
    async def get_current_weather_forcast(
            self,
            location: str | tuple[float, float],
            language: str = "ru",
    ) -> Dict[str, Any]:

        q = self._check_location_is_city_or_coords(location)
        params = {
            "key": self.api_key,
            "q": q,
            "days": 1,
            "lang": language,
        }

        endpoint = "forecast.json"
        url = urljoin(self.base_url, endpoint)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(url=url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    data = await response.json()
                    logger.info("Successful get current weather with: %s", q)
                    return data
            except aiohttp.ClientConnectionError as e:
                logger.error("Connection error: %s", e)
                raise
            except aiohttp.ClientError as e:
                logger.error("Network error: %s", e)
                raise
            except asyncio.TimeoutError:
                logger.error("Timeout requesting weather for location: %s", q)
                raise


if __name__ == '__main__':
    from config.config import get_config

    config = get_config()
    test_weather = WeatherService(config.weather.token, config.weather.base_url)
    print(asyncio.run(test_weather.get_current_weather(location="Kaliningrad")))
