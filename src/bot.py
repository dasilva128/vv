from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import logging
from src.utils import load_config, TELEGRAM_TOKEN
from src.db import init_db, get_configs_by_region, cleanup_old_configs
from src.link_collector import collect_v2ray_links
import os
import asyncio

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("فقط ادمین می‌تونه از این ربات استفاده کنه!")
        return
    await update.message.reply_text("سلام! با /region یه منطقه انتخاب کن.")

async def region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("فقط ادمین می‌تونه از این ربات استفاده کنه!")
        return

    # مناطق نمونه (می‌تونی از دیتابیس بخونی)
    regions = ["US", "DE", "IR", "Unknown", "All"]
    keyboard = [
        [InlineKeyboardButton(region, callback_data=f"region_{region}")]
        for region in regions
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("یه منطقه انتخاب کن:", reply_markup=reply_markup)

async def region_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.callback_query.answer("فقط ادمین می‌تونه از این ربات استفاده کنه!")
        return

    query = update.callback_query
    await query.answer()
    region = query.data.replace("region_", "")
    config = load_config()
    db_path = config["database"]["path"]
    max_configs = config["limits"]["max_configs_per_region"] if region != "All" else 1000

    configs = get_configs_by_region(db_path, region, max_configs)
    if not configs:
        await query.message.reply_text("هیچ کانفیگی برای این منطقه پیدا نشد!")
        return

    # ذخیره کانفیگ‌ها در فایل
    file_path = f"cache/{region}_configs.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        for config in configs:
            f.write(config + "\n")

    # ارسال فایل
    with open(file_path, "rb") as f:
        await query.message.reply_document(
            document=f,
            caption=f"کانفیگ‌های منطقه {region} ({len(configs)} تا)"
        )
    os.remove(file_path)
    logger.info(f"فایل کانفیگ‌های {region} برای کاربر {update.effective_user.id} ارسال شد.")

def is_admin(user_id):
    config = load_config()
    return user_id in config["telegram"]["admin_ids"]

async def update_configs(context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    db_path = config["database"]["path"]
    cleanup_old_configs(db_path, config["schedule"]["cleanup_interval"])
    collect_v2ray_links(db_path)
    logger.info("جمع‌آوری و پاکسازی لینک‌ها انجام شد.")

def main():
    config = load_config()
    db_path = config["database"]["path"]
    init_db(db_path)

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("region", region))
    app.add_handler(CallbackQueryHandler(region_callback, pattern="^region_"))

    # زمان‌بندی جمع‌آوری لینک‌ها
    app.job_queue.run_repeating(
        update_configs,
        interval=config["schedule"]["update_interval"],
        first=0
    )

    app.run_polling()

if __name__ == "__main__":
    main()