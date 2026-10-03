"""
analytics_service.py
Lightweight, read-only analytics built on top of DatabaseManager. Kept
intentionally simple per the project scope: top objects, per-source counts,
and overall totals for the dashboard and results screens.
"""
from typing import Dict, List, Tuple

from database import DatabaseManager


class AnalyticsService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def summary(self) -> Dict:
        """Overall totals used by the dashboard's stat cards."""
        return self.db.get_stats()

    def top_objects(self, limit: int = 5) -> List[Tuple[str, int]]:
        """The most frequently detected object labels, most common first."""
        stats = self.db.get_stats()
        label_counts = stats.get("label_counts", {})
        return sorted(label_counts.items(), key=lambda item: item[1], reverse=True)[:limit]

    def counts_by_source(self) -> Dict[str, int]:
        stats = self.db.get_stats()
        return stats.get("by_source", {})

    def recent_sessions(self, limit: int = 10) -> List[Dict]:
        return self.db.get_history(limit=limit)
