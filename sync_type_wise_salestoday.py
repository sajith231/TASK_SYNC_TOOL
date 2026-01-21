#!/usr/bin/env python3
"""
TYPE WISE SALES TODAY SYNC
Fetches present-day sales rows from acc_invmast
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
        logging.info("✅ DB connected (TYPE_WISE_SALES_TODAY)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB connection closed (TYPE_WISE_SALES_TODAY)")

    def fetch_type_wise_sales_today(self):
        query = """
            SELECT
                type     AS TYPE,
                nettotal AS NETTOTAL,
                billno   AS BILLNO,
                invdate  AS INVDATE
            FROM DBA.acc_invmast
            WHERE billno > 0
              AND invdate = CURRENT DATE
            ORDER BY billno
        """
        cur = self.conn.cursor()
        cur.execute(query)

        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]

        logging.info(f"📊 Fetched {len(rows)} type wise sales rows")
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
# ENTRY POINT (GUI ENABLED)
# ===============================
def run_type_wise_sales_today(config, gui_callback=None):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing TYPE WISE SALES TODAY...")
        db.connect()

        data = db.fetch_type_wise_sales_today()

        # 🔥 SEND TO GUI
        if gui_callback:
            gui_callback("type_wise_sales_today", len(data))

        if not data:
            logging.info("ℹ️ No type wise sales found for today")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ Type Wise Sales Today Sync failed")
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
    run_type_wise_sales_today(cfg)
