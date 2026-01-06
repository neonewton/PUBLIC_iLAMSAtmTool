import pytest
from unittest.mock import MagicMock, patch

from core.backend_1_Lesson_Link_Upload import run_elentra_link_upload


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def dummy_log_callback(entry):
    pass


def dummy_progress_callback(current, total):
    pass


# -------------------------------------------------
# VALIDATION TESTS
# -------------------------------------------------

def test_empty_inputs_raise():
    with pytest.raises(ValueError):
        run_elentra_link_upload(
            lams_lesson_titles_raw="",
            elentra_event_ids_raw="",
            lams_lesson_ids_raw="",
            upload_student=True,
            upload_monitor=True,
        )


def test_length_mismatch_raise():
    with pytest.raises(ValueError):
        run_elentra_link_upload(
            lams_lesson_titles_raw="Lesson A\nLesson B",
            lams_lesson_ids_raw="100",
            elentra_event_ids_raw="200\n201",
            upload_student=True,
            upload_monitor=True,
        )


def test_non_integer_lams_lesson_id():
    with pytest.raises(ValueError):
        run_elentra_link_upload(
            lams_lesson_titles_raw="Lesson A",
            lams_lesson_ids_raw="ABC",
            elentra_event_ids_raw="200",
            upload_student=True,
            upload_monitor=True,
        )


def test_non_integer_elentra_event_id():
    with pytest.raises(ValueError):
        run_elentra_link_upload(
            lams_lesson_titles_raw="Lesson A",
            lams_lesson_ids_raw="100",
            elentra_event_ids_raw="XYZ",
            upload_student=True,
            upload_monitor=True,
        )


# -------------------------------------------------
# STOP REQUEST HANDLING
# -------------------------------------------------

@patch("core.backend_1_Lesson_Link_Upload.st")
def test_stop_requested_immediate_exit(mock_st):
    """
    If stop_requested is already True, Selenium should never run.
    """
    mock_st.session_state = {"stop_requested": True}

    logs = run_elentra_link_upload(
        lams_lesson_titles_raw="Lesson A",
        lams_lesson_ids_raw="100",
        elentra_event_ids_raw="200",
        upload_student=True,
        upload_monitor=True,
    )

    assert isinstance(logs, list)
    assert any("Stop requested" in l["message"] for l in logs)


# -------------------------------------------------
# SELENIUM IS FULLY MOCKED
# -------------------------------------------------

@patch("core.backend_1_Lesson_Link_Upload.get_driver")
@patch("core.backend_1_Lesson_Link_Upload.st")
def test_driver_called_once(mock_st, mock_get_driver):
    """
    Verify Selenium driver is requested once for valid input.
    """
    mock_st.session_state = {"stop_requested": False}

    dummy_driver = MagicMock()
    dummy_wait = MagicMock()
    mock_get_driver.return_value = (dummy_driver, dummy_wait)

    result = run_elentra_link_upload(
        lams_lesson_titles_raw="Lesson A",
        lams_lesson_ids_raw="100",
        elentra_event_ids_raw="200",
        upload_student=False,
        upload_monitor=False,
        log_callback=dummy_log_callback,
        progress_callback=dummy_progress_callback,
    )

    mock_get_driver.assert_called_once()
    assert "logs" in result
    assert "results" in result


# -------------------------------------------------
# MULTI-ROW PROCESSING
# -------------------------------------------------

@patch("core.backend_1_Lesson_Link_Upload.get_driver")
@patch("core.backend_1_Lesson_Link_Upload.st")
def test_multiple_rows_progress(mock_st, mock_get_driver):
    mock_st.session_state = {"stop_requested": False}

    dummy_driver = MagicMock()
    dummy_wait = MagicMock()
    mock_get_driver.return_value = (dummy_driver, dummy_wait)

    progress_calls = []

    def progress_cb(current, total):
        progress_calls.append((current, total))

    run_elentra_link_upload(
        lams_lesson_titles_raw="Lesson A\nLesson B",
        lams_lesson_ids_raw="100\n101",
        elentra_event_ids_raw="200\n201",
        upload_student=False,
        upload_monitor=False,
        log_callback=dummy_log_callback,
        progress_callback=progress_cb,
    )

    assert progress_calls
    assert progress_calls[-1] == (2, 2)


# -------------------------------------------------
# LOG STRUCTURE GUARANTEE
# -------------------------------------------------

@patch("core.backend_1_Lesson_Link_Upload.get_driver")
@patch("core.backend_1_Lesson_Link_Upload.st")
def test_log_schema(mock_st, mock_get_driver):
    mock_st.session_state = {"stop_requested": False}

    dummy_driver = MagicMock()
    dummy_wait = MagicMock()
    mock_get_driver.return_value = (dummy_driver, dummy_wait)

    result = run_elentra_link_upload(
        lams_lesson_titles_raw="Lesson A",
        lams_lesson_ids_raw="100",
        elentra_event_ids_raw="200",
        upload_student=False,
        upload_monitor=False,
    )

    logs = result["logs"]
    assert logs

    required_keys = {"time", "module", "level", "message"}
    assert required_keys.issubset(logs[0].keys())
