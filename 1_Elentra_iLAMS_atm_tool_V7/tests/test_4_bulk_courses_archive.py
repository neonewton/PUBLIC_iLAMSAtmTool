
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from core.backend_4_Bulk_Courses_Archive import run_bulk_course_archive


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def fake_cell(text):
    el = MagicMock()
    el.text = text
    return el


def make_wait_with_rows(rows):
    """
    Configure wait.until(...) to return cells sequentially.
    """
    wait = MagicMock()
    wait.until.side_effect = rows
    return wait


# -------------------------------------------------
# BASIC FLOW / DRIVER
# -------------------------------------------------

@patch("core.backend_4_Bulk_Courses_Archive.get_driver")
def test_driver_attached_and_logs(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()
    mock_get_driver.return_value = (driver, wait)

    result = run_bulk_course_archive(
        excluded_ids=[],
        dry_run=True,
        max_courses=1,
    )

    assert "logs" in result
    assert any("Excluded IDs" in l["message"] for l in result["logs"])


# -------------------------------------------------
# DRY RUN MODE
# -------------------------------------------------

@patch("core.backend_4_Bulk_Courses_Archive._get_visible_row_count")
@patch("core.backend_4_Bulk_Courses_Archive.get_driver")
def test_dry_run_produces_audit_only(mock_get_driver, mock_row_count):
    driver = MagicMock()
    wait = MagicMock()
    mock_get_driver.return_value = (driver, wait)

    mock_row_count.r
