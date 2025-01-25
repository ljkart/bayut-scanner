from typing import Tuple
import re


def validate_location(location: str) -> bool:
    """
    Validate the location input
    Returns True if location is valid, False otherwise
    """
    if not location or len(location.strip().split(",")) < 2:
        return False

    # # Basic validation for common special characters
    # if re.search(r"[^a-zA-Z0-9\s\-]", location):
    #     return False

    return True


def cache_key(location: str, price_range: Tuple[int, int], rooms: str) -> str:
    """
    Generate a cache key based on search parameters
    """
    return f"{location.lower()}_{price_range[0]}_{price_range[1]}_{rooms}"
