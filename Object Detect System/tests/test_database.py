"""
tests/test_database.py
Basic tests for DatabaseManager. These only exercise database.py and
models.py, neither of which import Flet/OpenCV/YOLO, so they run without
the full requirements.txt installed (just `pip install pytest`).

Run with:  pytest tests/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from database import DatabaseManager
from models import DetectedObject, DetectionResult


@pytest.fixture()
def db(tmp_path):
    return DatabaseManager(db_path=str(tmp_path / "test.db"))


def _sample_result(source_type="image", source_name="cat.jpg"):
    return DetectionResult(
        source_type=source_type,
        source_name=source_name,
        objects=[
            DetectedObject(label="cat", confidence=0.91, bbox=(10, 10, 100, 100)),
            DetectedObject(label="cat", confidence=0.77, bbox=(150, 20, 220, 120)),
            DetectedObject(label="chair", confidence=0.63, bbox=(0, 0, 50, 50)),
        ],
        processing_time_ms=42.5,
    )


def test_save_and_fetch_history(db):
    session_id = db.save_detection_result(_sample_result())
    assert session_id > 0

    history = db.get_history()
    assert len(history) == 1
    row = history[0]
    assert row["source_name"] == "cat.jpg"
    assert row["object_count"] == 3
    assert row["max_confidence"] == pytest.approx(0.91)


def test_session_objects_persisted(db):
    session_id = db.save_detection_result(_sample_result())
    objects = db.get_session_objects(session_id)
    labels = sorted(o["label"] for o in objects)
    assert labels == ["cat", "cat", "chair"]


def test_stats_aggregate_across_sessions(db):
    db.save_detection_result(_sample_result(source_type="image", source_name="a.jpg"))
    db.save_detection_result(_sample_result(source_type="video", source_name="b.mp4"))

    stats = db.get_stats()
    assert stats["total_sessions"] == 2
    assert stats["total_objects"] == 6
    assert stats["label_counts"]["cat"] == 4
    assert stats["by_source"] == {"image": 1, "video": 1}


def test_delete_session_removes_objects(db):
    session_id = db.save_detection_result(_sample_result())
    db.delete_session(session_id)
    assert db.get_history() == []
    assert db.get_session_objects(session_id) == []


def test_clear_all(db):
    db.save_detection_result(_sample_result())
    db.save_detection_result(_sample_result(source_name="d.jpg"))
    db.clear_all()
    assert db.get_history() == []
    assert db.get_stats()["total_sessions"] == 0


def test_result_helper_properties():
    result = _sample_result()
    assert result.object_count == 3
    assert result.average_confidence == pytest.approx((0.91 + 0.77 + 0.63) / 3)
    assert result.highest_confidence == pytest.approx(0.91)
    assert result.object_counts_by_label == {"cat": 2, "chair": 1}
