#!/usr/bin/env python3
"""
TENDER CASH SYNC
DBA.acc_tendercash + DBA.acc_currency → tendercash
"""

import logging
import traceback
from decimal import Decimal

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
        self.conn = pyodbc.connect(
            f"DSN={self.config.dsn};"
            f"UID={self.config.username};"
            f"PWD={self.config.password};"
        )
        logging.info("✅ DB connected (TENDERCASH)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB connection closed (TENDERCASH)")

    def fetch_tendercash(self):
        query = """
            SELECT
                t.mslno,
                t.code            AS tender_code,
                t.amount,
                c.code            AS currency_code,
                c.name            AS currency_name
            FROM DBA.acc_tendercash t
            LEFT JOIN DBA.acc_currency c
                ON t.code = c.code
        """

        cur = self.conn.cursor()
        cur.execute(query)

        cols = [c[0] for c in cur.description]
        rows = []

        for r in cur.fetchall():
            row = dict(zip(cols, r))

            # 🔥 Decimal → float
            for k, v in row.items():
                if isinstance(v, Decimal):
                    row[k] = float(v)

            rows.append(row)

        logging.info(f"📦 Fetched {len(rows)} tendercash rows")
        return rows


# ===============================
# API CLIENT
# ===============================
class APIClient:
    ENDPOINT = "/upload-tendercash/"

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

        logging.info(f"✅ Uploaded {len(data)} tendercash rows")


# ===============================
# ENTRY POINT (CALLED FROM sync.py)
# ===============================
def run_tendercash_sync(config):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing TENDERCASH...")
        db.connect()

        data = db.fetch_tendercash()

        if not data:
            logging.info("ℹ️ No tendercash data found")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ TENDERCASH sync failed")
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
    run_tendercash_sync(cfg)
