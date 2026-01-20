#!/usr/bin/env python3
"""
STOCK REPORT SYNC
acc_product + acc_productbatch → stock_report

RULE:
- If total rows > 20000 → DO NOT SYNC
- 20000 is allowed
"""

import logging
import traceback
from decimal import Decimal

import pyodbc
import requests


# ===============================
# CONSTANTS
# ===============================
MAX_STOCK_ROWS = 20000


# ===============================
# DATABASE
# ===============================
class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        self.conn = pyodbc.connect(
            f"DSN={self.config.dsn};"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
        )
        logging.info("✅ DB connected (STOCK REPORT)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB connection closed (STOCK REPORT)")

    def fetch_stock_report(self):
        query = """
            SELECT
                p.code       AS product_code,
                p.name       AS product_name,
                b.productcode,
                b.barcode,
                b.bmrp,
                b.salesprice,
                b.quantity
            FROM DBA.acc_product p
            JOIN DBA.acc_productbatch b
                ON p.code = b.productcode
        """

        cur = self.conn.cursor()
        cur.execute(query)

        cols = [c[0] for c in cur.description]
        rows = []

        for r in cur.fetchall():
            row = dict(zip(cols, r))

            # Convert Decimal → float
            for k, v in row.items():
                if isinstance(v, Decimal):
                    row[k] = float(v)

            rows.append(row)

        logging.info(f"📦 Fetched {len(rows)} stock report rows")
        return rows


# ===============================
# API CLIENT
# ===============================
class APIClient:
    ENDPOINT = "/upload-stock-report/"

    def __init__(self, config):
        self.config = config

    def upload(self, data):
        url = (
            f"{self.config.api_base_url}"
            f"{self.ENDPOINT}"
            f"?client_id={self.config.client_id}"
        )

        logging.info(f"🌐 POST {url}")
        res = requests.post(
            url,
            json=data,
            timeout=self.config.api_timeout
        )

        if res.status_code not in (200, 201):
            raise Exception(res.text)

        logging.info(f"✅ Uploaded {len(data)} stock report rows")


# ===============================
# ENTRY POINT (CALLED FROM sync.py)
# ===============================
def run_stock_report_sync(config):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing STOCK REPORT...")
        db.connect()

        data = db.fetch_stock_report()

        if not data:
            logging.info("ℹ️ No stock report data found")
            return

        total_rows = len(data)

        # 🔥 HARD LIMIT CHECK
        if total_rows > MAX_STOCK_ROWS:
            logging.warning(
                f"⚠️ STOCK REPORT sync skipped! "
                f"Row count {total_rows} exceeds limit {MAX_STOCK_ROWS}"
            )
            return

        logging.info(
            f"📦 Stock report row count {total_rows} within limit "
            f"({MAX_STOCK_ROWS}). Proceeding with sync..."
        )

        api.upload(data)

    except Exception:
        logging.error("❌ STOCK REPORT sync failed")
        logging.error(traceback.format_exc())
        raise
    finally:
        db.close()


# ===============================
# OPTIONAL STANDALONE RUN
# ===============================
if __name__ == "__main__":
    from sync import DatabaseConfig

    logging.basicConfig(level=logging.INFO)
    cfg = DatabaseConfig()
    run_stock_report_sync(cfg)
