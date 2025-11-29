import logging

from typing import Dict, Any

logger = logging.getLogger(__name__)


def parse_city(city_data: Dict[str, Any]) -> tuple[str, str]:
    try:
        city_name = city_data['name']
        city_full_name = city_data['display_name']

        city_info = f"{city_name},\n{city_full_name}"
        return city_info, city_name

    except Exception as e:
        logger.error(e)
        raise
