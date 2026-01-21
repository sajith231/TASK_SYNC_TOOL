#!/usr/bin/env python3
"""
REFRESH TAG SYNC
LAST 3 DAYS ONLY (Today + 2 days back)
"""

import logging
import traceback
from decimal import Decimal
from datetime import date, timedelta

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
        logging.info("✅ DB connected (REFRESH TAG)")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("🔒 DB closed (REFRESH TAG)")

    def fetch_refresh_tag(self):
        from_date = date.today() - timedelta(days=2)

        query = f"""
            SELECT
                edate,
                etime,
                userid,
                remark
            FROM DBA.acc_refreshtag
            WHERE edate >= '{from_date}'
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
            rows.append(row)

        logging.info(f"📦 Fetched {len(rows)} refresh tag rows")
        return rows


class APIClient:
    ENDPOINT = "/upload-refresh-tag/"

    def __init__(self, config):
        self.config = config

    def upload(self, data):
        url = (
            f"{self.config.api_base_url}"
            f"{self.ENDPOINT}"
            f"?client_id={self.config.client_id}"
        )

        logging.info(f"🌐 POST {url}")
        res = requests.post(url, json=data, timeout=self.config.api_timeout)

        if res.status_code not in (200, 201):
            raise Exception(res.text)

        logging.info("✅ Refresh tag uploaded successfully")


def run_refresh_tag_sync(config):
    db = Database(config)
    api = APIClient(config)

    try:
        logging.info("🔄 Syncing REFRESH TAG...")
        db.connect()

        data = db.fetch_refresh_tag()
        if not data:
            logging.info("ℹ️ No refresh tag data found")
            return

        api.upload(data)

    except Exception:
        logging.error("❌ REFRESH TAG sync failed")
        logging.error(traceback.format_exc())
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from sync import DatabaseConfig

    logging.basicConfig(level=logging.INFO)
    cfg = DatabaseConfig()
    run_refresh_tag_sync(cfg)
