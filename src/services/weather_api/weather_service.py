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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
           retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)))
    async def get_current_weather(
            self,
            city: str | None = None,
            coords: tuple[float, float] | None = None,
            language: str = "ru",
    ) -> Dict[str, Any]:

        if city is None:
            q = f"{coords[0]},{coords[1]}"
        else:
            q = city

        params = {
            "key": self.api_key,
            "q": q,
            "lang": language,
        }
        endpoint = "current.json"
        url = urljoin(self.base_url, endpoint)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successful get current weather with: {q}")
                        return data

                    elif response.status == 400:
                        error_text = await response.text()
                        logger.error("Bad request for location '%s'. Status: %s, Response: %.200s",
                                     q, response.status, error_text)
                        raise ValueError(f"Bad request for {q}: {error_text}")

                    elif response.status == 401:
                        logger.error("Authentication failed for '%s'. Invalid API key", q)
                        raise PermissionError("Invalid API key")

                    elif response.status == 404:
                        logger.warning("Place '%s' not found", q)
                        raise ValueError(f"Place '{q}' not found")

                    elif response.status == 500:
                        logger.error("Internal server error for '%s'. Status: %s", q, response.status)
                        raise Exception(f"Internal server error: {response.status}")

                    else:
                        logger.error("Unexpected API error for '%s'. Status: %s",
                                     q, response.status)
                        raise Exception(f"API error {response.status}")

            except aiohttp.ClientError as e:
                logger.error(f"Network error for {q}: {e}")
                raise Exception(f"Network error: {e}")

            except asyncio.TimeoutError:
                logger.error(f"Timeout requesting weather for {q}")
                raise Exception("Request timeout")


if __name__ == '__main__':
    from config.config import get_config

    config = get_config()
    test_weather = WeatherService(config.weather.token, config.weather.base_url)
    print(asyncio.run(test_weather.get_current_weather(coords=(54.71, 20.5))))
