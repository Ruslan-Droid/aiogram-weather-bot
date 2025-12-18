import asyncio
import logging
import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from src.services.open_street_map_api.city_parsing import parse_city

logger = logging.getLogger(__name__)


class CityService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def _city_parsing(city: str) -> str:
        return city.strip().lower()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1),
           retry=retry_if_exception_type(aiohttp.ClientConnectionError))
    async def check_city(
            self,
            city_name: str
    ) -> tuple[str, str] | None:
        city = self._city_parsing(city_name)

        params = {
            "q": city,
            "format": "jsonv2",
            "limit": 1,
        }

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(url=self.base_url, params=params,
                                       timeout=aiohttp.ClientTimeout(total=30)) as response:
                    data = await response.json()
                    logger.info("Successful get current city with: %s", city_name)
                    if data and len(data) > 0:
                        return parse_city(data[0])
                    else:
                        logger.warning("City not found: %s", city_name)
                        return None

            except aiohttp.ClientConnectionError as e:
                logger.error("Connection error: %s", e)
                raise
            except aiohttp.ClientError as e:
                logger.error("Network error: %s", e)
                raise
            except asyncio.TimeoutError:
                logger.error("Timeout requesting for city: %s", city_name)
                raise


if __name__ == '__main__':
    city_service = CityService(base_url='https://nominatim.openstreetmap.org/search')
    asyncio.run(city_service.check_city("Москва"))
