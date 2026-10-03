"""
database.py
Lightweight SQLite persistence for detection history and statistics.
All queries are parameterized. Connections are opened per-operation
(SQLite handles this cheaply) so the service is safe to call from the
worker threads used for live detection and background video processing.
"""
import logging
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional

import config
from models import DetectionResult

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS detection_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,
    source_name TEXT NOT NULL,
    object_count INTEGER NOT NULL DEFAULT 0,
    avg_confidence REAL NOT NULL DEFAULT 0,
    max_confidence REAL NOT NULL DEFAULT 0,
    processing_time_ms REAL NOT NULL DEFAULT 0,
    output_path TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS detected_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES detection_sessions(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    confidence REAL NOT NULL,
    x1 REAL, y1 REAL, x2 REAL, y2 REAL
);

CREATE INDEX IF NOT EXISTS idx_objects_session ON detected_objects(session_id);
CREATE INDEX IF NOT EXISTS idx_objects_label ON detected_objects(label);
CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON detection_sessions(timestamp);
"""


class DatabaseError(Exception):
    pass


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or config.DB_PATH)
        self._lock = threading.Lock()
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as conn:
                conn.executescript(_SCHEMA)
        except sqlite3.Error as e:
            logger.exception("Failed to initialize database")
            raise DatabaseError(f"Could not initialize database: {e}") from e

    # -- Writes ------------------------------------------------------------

    def save_detection_result(self, result: DetectionResult) -> int:
        """Persist a DetectionResult and its individual objects. Returns the
        new session id."""
        try:
            with self._lock, self._connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO detection_sessions
                        (source_type, source_name, object_count, avg_confidence,
                         max_confidence, processing_time_ms, output_path, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime(?))
                    """,
                    (
                        result.source_type,
                        result.source_name,
                        result.object_count,
                        result.average_confidence,
                        result.highest_confidence,
                        result.processing_time_ms,
                        result.output_path,
                        result.timestamp.isoformat(sep=" "),
                    ),
                )
                session_id = cur.lastrowid
                if result.objects:
                    conn.executemany(
                        """
                        INSERT INTO detected_objects
                            (session_id, label, confidence, x1, y1, x2, y2)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (session_id, o.label, o.confidence, *o.bbox)
                            for o in result.objects
                        ],
                    )
                return session_id
        except sqlite3.Error as e:
            logger.exception("Failed to save detection result")
            raise DatabaseError(f"Could not save detection result: {e}") from e

    def delete_session(self, session_id: int) -> None:
        try:
            with self._lock, self._connect() as conn:
                conn.execute(
                    "DELETE FROM detection_sessions WHERE id = ?", (session_id,)
                )
        except sqlite3.Error as e:
            logger.exception("Failed to delete session %s", session_id)
            raise DatabaseError(f"Could not delete session: {e}") from e

    def clear_all(self) -> None:
        try:
            with self._lock, self._connect() as conn:
                conn.execute("DELETE FROM detected_objects")
                conn.execute("DELETE FROM detection_sessions")
        except sqlite3.Error as e:
            logger.exception("Failed to clear history")
            raise DatabaseError(f"Could not clear history: {e}") from e

    # -- Reads ---------------------------------------------------------------

    def get_history(self, limit: int = 50, source_type: Optional[str] = None) -> List[Dict]:
        try:
            with self._connect() as conn:
                if source_type:
                    rows = conn.execute(
                        """
                        SELECT * FROM detection_sessions
                        WHERE source_type = ?
                        ORDER BY timestamp DESC, id DESC LIMIT ?
                        """,
                        (source_type, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT * FROM detection_sessions
                        ORDER BY timestamp DESC, id DESC LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.exception("Failed to fetch history")
            raise DatabaseError(f"Could not load history: {e}") from e

    def get_session_objects(self, session_id: int) -> List[Dict]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM detected_objects WHERE session_id = ? ORDER BY confidence DESC",
                    (session_id,),
                ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.exception("Failed to fetch session objects")
            raise DatabaseError(f"Could not load session details: {e}") from e

    def get_stats(self) -> Dict:
        """Lightweight aggregate stats used by the dashboard and analytics."""
        try:
            with self._connect() as conn:
                total_sessions = conn.execute(
                    "SELECT COUNT(*) AS c FROM detection_sessions"
                ).fetchone()["c"]
                total_objects = conn.execute(
                    "SELECT COALESCE(SUM(object_count), 0) AS c FROM detection_sessions"
                ).fetchone()["c"]
                avg_conf_row = conn.execute(
                    "SELECT AVG(confidence) AS a FROM detected_objects"
                ).fetchone()
                avg_confidence = avg_conf_row["a"] or 0.0

                label_rows = conn.execute(
                    """
                    SELECT label, COUNT(*) AS c FROM detected_objects
                    GROUP BY label ORDER BY c DESC
                    """
                ).fetchall()
                label_counts = {r["label"]: r["c"] for r in label_rows}

                by_source_rows = conn.execute(
                    """
                    SELECT source_type, COUNT(*) AS c FROM detection_sessions
                    GROUP BY source_type
                    """
                ).fetchall()
                by_source = {r["source_type"]: r["c"] for r in by_source_rows}

                return {
                    "total_sessions": total_sessions,
                    "total_objects": total_objects,
                    "avg_confidence": avg_confidence,
                    "label_counts": label_counts,
                    "by_source": by_source,
                }
        except sqlite3.Error as e:
            logger.exception("Failed to compute stats")
            raise DatabaseError(f"Could not compute statistics: {e}") from e
