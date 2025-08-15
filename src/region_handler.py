import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.utils import load_config
import json
import os

logger = logging.getLogger(__name__)

# کش ساده برای مناطق
region_cache = {}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_region(ip, api_url):
    response = requests.get(api_url.format(ip=ip), timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("country", "Unknown")

def get_region(ip):
    config = load_config()
    api_url = config["api"]["region_api"]
    cache_ttl = config["cache"]["ttl"]

    # بررسی کش
    if ip in region_cache:
        timestamp, region = region_cache[ip]
        if (datetime.now() - timestamp).total_seconds() < cache_ttl:
            return region

    try:
        region = fetch_region(ip, api_url)
        region_cache[ip] = (datetime.now(), region)
        return region
    except Exception as e:
        logger.error(f"خطا در گرفتن منطقه برای IP {ip}: {e}")
        return "Unknown"