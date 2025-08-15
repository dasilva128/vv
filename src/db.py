import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config TEXT NOT NULL,
            region TEXT,
            timestamp DATETIME
        )
    """)
    conn.commit()
    conn.close()

def save_config(db_path, config, region):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO configs (config, region, timestamp) VALUES (?, ?, ?)",
        (config, region, datetime.now())
    )
    conn.commit()
    conn.close()

def get_configs_by_region(db_path, region, limit):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if region.lower() == "all":
        c.execute("SELECT config FROM configs ORDER BY timestamp DESC LIMIT ?", (limit,))
    else:
        c.execute("SELECT config FROM configs WHERE region = ? ORDER BY timestamp DESC LIMIT ?",
                  (region, limit))
    configs = [row[0] for row in c.fetchall()]
    conn.close()
    return configs

def cleanup_old_configs(db_path, hours):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    threshold = datetime.now() - timedelta(hours=hours)
    c.execute("DELETE FROM configs WHERE timestamp < ?", (threshold,))
    conn.commit()
    conn.close()