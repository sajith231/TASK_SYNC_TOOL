#!/usr/bin/env python3
"""
PDC SYNC
Only COLNSTATUS = 'N'
"""

import logging
import traceback
from decimal import Decimal
from datetime import date, datetime

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
        logging.info("✅ DB connected (PDC)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB closed (PDC)")

    def fetch_pdc(self):
        query = """
            SELECT
                colndate,
                party,
                amount,
                chequedate,
                chequeno,
                colnstatus,
                status
            FROM DBA.acc_cheques
            WHERE colnstatus = 'N'
        """

        cur = self.conn.cursor()
        cur.execute(query)

        cols = [c[0] for c in cur.description]
        rows = []

        for r in cur.fetchall():
            row = dict(zip(cols, r))

            for k, v in row.items():
                if isinstance(v, Decimal):
                    row[k] = float(v)
                elif isinstance(v, (date, datetime)):
                    row[k] = v.isoformat()

            rows.append(row)

        logging.info(f"📦 Fetched {len(rows)} PDC rows")
        return rows


# ===============================
# API CLIENT
# ===============================
class APIClient:
    ENDPOINT = "/upload-pdc/"

    def __init__(self, config):
        self.config = config

    def upload(self, rows):
        url = f"{self.config.api_base_url}{self.ENDPOINT}"

        payload = {
            "client_id": self.config.client_id,
            "data": rows
        }

        logging.info(f"🌐 POST {url}")
        res = requests.post(
            url,
            json=payload,
            timeout=self.config.api_timeout
        )

        if res.status_code not in (200, 201):
            raise Exception(res.text)

        logging.info(f"✅ Uploaded {len(rows)} PDC records")


# ===============================
# ENTRY POINT (GUI ENABLED)
# ===============================
def run_pdc_sync(config, gui_callback=None):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing PDC...")
        db.connect()

        data = db.fetch_pdc()

        # 🔥 GUI CALLBACK
        if gui_callback:
            gui_callback("pdc", len(data))

        if not data:
            logging.info("ℹ️ No PDC data found")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ PDC sync failed")
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
    run_pdc_sync(cfg)
