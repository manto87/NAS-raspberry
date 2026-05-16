import sqlite3
from pathlib import Path

from .base_sensor import WeatherReading


def _connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            pressure    REAL
        )"""
    )
    conn.commit()
    return conn


def save(reading: WeatherReading, db_path: str):
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO readings (timestamp, temperature, humidity, pressure) VALUES (?,?,?,?)",
        (reading.timestamp.isoformat(), reading.temperature, reading.humidity, reading.pressure),
    )
    conn.commit()
    conn.close()


def get_latest(db_path: str) -> dict | None:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def get_history(db_path: str, hours: int = 24) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        """SELECT * FROM readings
           WHERE timestamp >= datetime('now', ?)
           ORDER BY timestamp ASC""",
        (f"-{hours} hours",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
