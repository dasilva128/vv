import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from src.utils import is_valid_v2ray_link, load_channels, load_config
from src.region_handler import get_region

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_url(url, proxy=None):
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(url, proxies=proxies, timeout=10)
    response.raise_for_status()
    return response

def collect_v2ray_links(db_path):
    config = load_config()
    proxy = config["telegram"].get("proxy")
    channels = load_channels()
    configs = []

    for url in channels:
        try:
            response = fetch_url(url, proxy)
            soup = BeautifulSoup(response.content, "html.parser")
            code_tags = soup.find_all("code")

            for tag in code_tags:
                text = tag.get_text().strip()
                if is_valid_v2ray_link(text):
                    configs.append(text)
                    address = parse_v2ray_address(text)
                    if address:
                        region = get_region(address)
                        save_config(db_path, text, region)
                    else:
                        save_config(db_path, text, "Unknown")
            logger.info(f"جمع‌آوری لینک‌ها از {url} انجام شد.")
        except Exception as e:
            logger.error(f"خطا در جمع‌آوری لینک‌ها از {url}: {e}")

    return configs