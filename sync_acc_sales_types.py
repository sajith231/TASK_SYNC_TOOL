#!/usr/bin/env python3
"""
ACC SALES TYPES SYNC
Syncs cd + name from DBA.acc_sales_types to Web API
"""

import logging
import traceback
import pyodbc
import requests


# ===============================
# DATABASE
# ===============================
class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        conn_str = (
            f"DSN={self.config.dsn};"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
        )
        self.conn = pyodbc.connect(conn_str)
        logging.info("✅ DB connected (ACC_SALES_TYPES)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB connection closed (ACC_SALES_TYPES)")

    def fetch_sales_types(self):
        query = """
            SELECT
                cd,
                name
            FROM DBA.acc_sales_types
        """
        cur = self.conn.cursor()
        cur.execute(query)

        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        logging.info(f"📊 Fetched {len(rows)} ACC sales types")
        return rows


# ===============================
# API CLIENT
# ===============================
class APIClient:
    ENDPOINT = "/upload-acc-sales-types/"

    def __init__(self, config):
        self.config = config

    def upload(self, data):
        base = self.config.api_base_url.rstrip("/")
        endpoint = self.ENDPOINT.lstrip("/")

        url = f"{base}/{endpoint}?client_id={self.config.client_id}"

        logging.info(f"🌐 POST {url}")

        res = requests.post(url, json=data, timeout=self.config.api_timeout)

        if res.status_code not in (200, 201):
            raise Exception(res.text)

        logging.info(f"✅ Uploaded {len(data)} ACC sales types")



# ===============================
# ENTRY POINT
# ===============================
def run_acc_sales_types_sync(config, gui_callback=None):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing ACC SALES TYPES...")
        db.connect()

        data = db.fetch_sales_types()

        # 🔥 SEND TO GUI
        if gui_callback:
            gui_callback("acc_sales_types", len(data))

        if not data:
            logging.info("ℹ️ No ACC sales types found")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ ACC SALES TYPES Sync failed")
        logging.error(traceback.format_exc())
        raise
    finally:
        db.close()


# ===============================
# STANDALONE RUN
# ===============================
if __name__ == "__main__":
    from sync import DatabaseConfig

    logging.basicConfig(level=logging.INFO)
    cfg = DatabaseConfig()
    run_acc_sales_types_sync(cfg)
