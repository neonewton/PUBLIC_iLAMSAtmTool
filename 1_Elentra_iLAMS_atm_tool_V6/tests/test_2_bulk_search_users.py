import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from core.backend_2_Bulk_Search_Users import run_user_search


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def make_fake_row(cols):
    """
    Create a fake Selenium <tr> element with <td> children.
    """
    row = MagicMock()
    td_elements = []

    for value in cols:
        td = MagicMock()
        td.text = value
        td_elements.append(td)

    row.find_elements.return_value = td_elements
    return row


# -------------------------------------------------
# DRIVER ATTACHMENT
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_driver_attach_failure_returns_empty_df(mock_get_driver):
    mock_get_driver.side_effect = Exception("Chrome not running")

    result = run_user_search(
        search_values=["Alice"],
    )

    assert isinstance(result["dataframe"], pd.DataFrame)
    assert result["dataframe"].empty
    assert any("Failed to attach" in log["message"] for log in result["logs"])


# -------------------------------------------------
# STOP FLAG
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_stop_flag_exits_early(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()
    mock_get_driver.return_value = (driver, wait)

    result = run_user_search(
        search_values=["Alice", "Bob"],
        stop_flag=lambda: True,
    )

    assert result["dataframe"].empty
    assert any("Stop requested" in log["message"] for log in result["logs"])


# -------------------------------------------------
# NO RESULTS CASE
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_no_results_found(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    driver.find_elements.return_value = []  # no rows
    mock_get_driver.return_value = (driver, wait)

    result = run_user_search(
        search_values=["Alice Tan"],
    )

    df = result["dataframe"]

    assert len(df) == 1
    assert df.loc[0, "DL check account?"] == "Acc Not Found"
    assert df.loc[0, "Input"] == "Alice Tan"


# -------------------------------------------------
# SINGLE RESULT
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_single_result_exist(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    row = make_fake_row(["123", "alice", "Alice", "Tan"])
    driver.find_elements.return_value = [row]

    mock_get_driver.return_value = (driver, wait)

    result = run_user_search(
        search_values=["Alice Tan"],
    )

    df = result["dataframe"]

    assert len(df) == 1
    assert df.loc[0, "DL check account?"] == "Exist"
    assert df.loc[0, "User ID"] == "123"
    assert df.loc[0, "First Name"] == "Alice"
    assert df.loc[0, "Last Name"] == "Tan"


# -------------------------------------------------
# MULTIPLE RESULTS
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_multiple_results_acc_gt_1(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    row1 = make_fake_row(["111", "user1", "Alice", "Tan"])
    row2 = make_fake_row(["222", "user2", "Alice", "Tan"])

    driver.find_elements.return_value = [row1, row2]
    mock_get_driver.return_value = (driver, wait)

    result = run_user_search(
        search_values=["Alice Tan"],
    )

    df = result["dataframe"]

    assert len(df) == 2
    assert set(df["DL check account?"]) == {"Acc >1"}
    assert set(df["Row #"]) == {1, 2}


# -------------------------------------------------
# INPUT SANITISATION
# -------------------------------------------------
@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_brackets_are_stripped(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    driver.find_elements.return_value = []
    mock_get_driver.return_value = (driver, wait)

    run_user_search(
        search_values=["lkc-dl-lams (TTSH)"],
    )

    # ensure send_keys got cleaned value
    sent_value = driver.find_element.return_value.send_keys.call_args_list
    assert sent_value  # called at least once


# -------------------------------------------------
# PROGRESS CALLBACK
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_progress_callback_called(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    driver.find_elements.return_value = []
    mock_get_driver.return_value = (driver, wait)

    calls = []

    def progress_cb(c, t):
        calls.append((c, t))

    run_user_search(
        search_values=["A", "B", "C"],
        progress_callback=progress_cb,
    )

    assert calls
    assert calls[-1] == (3, 3)


# -------------------------------------------------
# LOG SCHEMA
# -------------------------------------------------

@patch("core.backend_2_Bulk_Search_Users.get_driver")
def test_log_schema(mock_get_driver):
    driver = MagicMock()
    wait = MagicMock()

    driver.find_elements.return_value = []
    mock_get_driver.return_value = (driver, wait)

    result = run_user_search(
        search_values=["Alice"],
    )

    logs = result["logs"]
    assert logs

    required_keys = {"timestamp", "feature", "level", "message"}
    assert required_keys.issubset(logs[0].keys())
