import logging
import yaml
import os
from dotenv import load_dotenv
import re
from urllib.parse import urlparse
import base64
import json

# تنظیم لاگینگ
logging.basicConfig(
    filename="logs/bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)

# لود تنظیمات
def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# لود لینک‌های کانال‌ها
def load_channels():
    with open("channels.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["channels"]

# لود توکن از .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# اعتبارسنجی لینک‌های V2Ray
def is_valid_v2ray_link(link):
    pattern = r"^(vmess|vless|hysteria2)://.+"
    return bool(re.match(pattern, link))

# استخراج آدرس سرور از لینک
def parse_v2ray_address(config):
    try:
        protocol = config.split("://")[0]
        if protocol == "vmess":
            # دیکد base64 برای vmess
            encoded = config.split("://")[1].split("#")[0]
            decoded = base64.b64decode(encoded).decode("utf-8")
            vmess_data = json.loads(decoded)
            return vmess_data.get("add")
        else:
            # برای vless و hysteria2
            parsed = urlparse(config)
            return parsed.netloc.split("@")[-1].split(":")[0]
    except Exception as e:
        logger.error(f"خطا در پارس آدرس از لینک: {e}")
        return None