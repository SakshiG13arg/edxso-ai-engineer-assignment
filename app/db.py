from __future__ import annotations
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

class OutreachDB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            campaign_id TEXT NOT NULL,
            message_generated INTEGER NOT NULL DEFAULT 0,
            sent INTEGER NOT NULL DEFAULT 0,
            sent_at TEXT,
            status TEXT NOT NULL,
            error TEXT,
            UNIQUE(influencer_id, channel, campaign_id)
        )""")
        self.conn.commit()

    def record(self, influencer_id, channel, campaign_id, message_generated, sent, status, error=None):
        now = datetime.now(timezone.utc).isoformat() if sent else None
        try:
            self.conn.execute("""INSERT INTO outreach
                (influencer_id, channel, campaign_id, message_generated, sent, sent_at, status, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (influencer_id, channel, campaign_id, int(message_generated), int(sent), now, status, error))
            self.conn.commit()
            return {"status": status, "duplicate": False}
        except sqlite3.IntegrityError:
            return {"status": "DUPLICATE_BLOCKED", "duplicate": True}

    def all(self):
        return self.conn.execute("SELECT * FROM outreach ORDER BY id DESC").fetchall()
