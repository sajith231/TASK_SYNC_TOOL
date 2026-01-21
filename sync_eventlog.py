#!/usr/bin/env python3
"""
EVENTLOG SYNC
Last 3 days (today + yesterday + day before)
"""

import logging
import traceback
from datetime import date, timedelta
from decimal import Decimal

import pyodbc
import requests


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
        logging.info("✅ DB connected (EVENTLOG)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB closed (EVENTLOG)")

    def fetch_eventlog(self):
        cur = self.conn.cursor()
        rows = []

        for i in range(3):
            d = date.today() - timedelta(days=i)
            table = f"zzevent{d.strftime('%Y%m%d')}"

            query = f"""
                SELECT uid, edate, etime, sevent
                FROM DBA.{table}
                WHERE LOWER(sevent) LIKE 'modify sales voucher%'
                   OR LOWER(sevent) LIKE 'sales voucher removed%'
            """

            try:
                cur.execute(query)

                for r in cur.fetchall():
                    row = dict(zip([c[0] for c in cur.description], r))

                    for k, v in row.items():
                        if isinstance(v, Decimal):
                            row[k] = float(v)
                        elif hasattr(v, "isoformat"):
                            row[k] = v.isoformat()

                    rows.append(row)

                logging.info(f"📦 {table}: {cur.rowcount} rows")

            except Exception:
                logging.warning(f"⚠️ Table not found: {table}")

        logging.info(f"📊 Total EVENTLOG rows: {len(rows)}")
        return rows


class APIClient:
    ENDPOINT = "/upload-eventlog/"

    def __init__(self, config):
        self.config = config

    def upload(self, data):
        url = f"{self.config.api_base_url}{self.ENDPOINT}"

        payload = {
            "client_id": self.config.client_id,
            "data": data
        }

        logging.info(f"🌐 POST {url}")
        res = requests.post(url, json=payload, timeout=60)

        if res.status_code not in (200, 201):
            raise Exception(res.text)

        logging.info(f"✅ Uploaded {len(data)} EVENTLOG rows")


def run_eventlog_sync(config):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing EVENTLOG...")
        db.connect()

        data = db.fetch_eventlog()
        if not data:
            logging.info("ℹ️ No EVENTLOG data")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ EVENTLOG sync failed")
        logging.error(traceback.format_exc())
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from sync import DatabaseConfig
    logging.basicConfig(level=logging.INFO)
    cfg = DatabaseConfig()
    run_eventlog_sync(cfg)
