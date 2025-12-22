import time
import pandas as pd
from typing import List, Dict, Callable, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)

from .selenium_utils import (
    get_driver,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
)
from .config import get_config


# ===== XPaths (based on your current iLAMS page) =====
ROWS_SELECT_XPATH = "/html/body/div/div/div/div/div[2]/div/table/tfoot/tr/th/select"
SORT_XPATH = '//*[@id="idsorter"]/div/div'

# Table rows on Org Manage Courses page
TABLE_ROW_XPATH = '//*[@id="content"]/div/div[2]/div/table/tbody/tr'

# Columns (relative to TABLE_ROW_XPATH[row_index])
ID_CELL_XPATH = TABLE_ROW_XPATH + "[{i}]/td[1]"
NAME_LINK_XPATH = TABLE_ROW_XPATH + "[{i}]/td[2]/a"

# Course edit flow XPaths (same as your original)
EDIT_XPATH = '//*[@id="editCourse"]'
STATUS_XPATH = '//*[@id="stateId"]'
SAVE_XPATH = '//*[@id="saveButton"]'
#lams_course_mgmt_url = "https://ilams.lamsinternational.com/lams/admin/orgmanage.do?org=1"
lams_course_mgmt_url = "https://ilams-bk.lamsinternational.com/lams/admin/orgmanage.do?org=1"

def _set_rows_per_page(wait, log_fn: Callable[[str, str], None], value_text: str = "100") -> None:
    """
    Set table page size using the footer select dropdown (e.g. 100 rows).
    """
    try:
        sel_el = wait.until(EC.presence_of_element_located((By.XPATH, ROWS_SELECT_XPATH)))
        Select(sel_el).select_by_visible_text(value_text)
        time.sleep(0.8)  # allow table to refresh
    except Exception as e:
        # Non-fatal: some pages may not have this control, but in your case it does.
        log_fn(f"Could not set rows-per-page to {value_text}: {e}", "warn")


def _click_sort_twice(wait, log_fn: Callable[[str, str], None]) -> None:
    """
    Re-sort by clicking sort header twice (matching your original behaviour).
    """
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, SORT_XPATH))).click()
        time.sleep(0.5)
        wait.until(EC.element_to_be_clickable((By.XPATH, SORT_XPATH))).click()
        time.sleep(0.5)
    except Exception as e:
        log_fn(f"Sort click failed (continuing): {e}", "warn")


def _get_visible_row_count(driver, log_fn: Callable[[str, str], None]) -> int:
    """
    Count how many rows are currently visible in tbody.
    Uses driver.find_elements to avoid hard failing on wait when empty.
    """
    try:
        rows = driver.find_elements(By.XPATH, TABLE_ROW_XPATH)
        return len(rows)
    except Exception as e:
        log_fn(f"Failed to count table rows: {e}", "warn")
        return 0


def run_bulk_course_archive(
    excluded_ids: List[str],
    dry_run: bool,
    max_courses: int,
    log_callback=default_log_callback,
    progress_callback=default_progress_callback,
    pause_flag: Callable[[], bool] = lambda: False,
    stop_flag: Callable[[], bool] = lambda: False,
) -> Dict:
    """
    Bulk archive iLAMS courses with Pause / Resume / Stop support.

    Behaviour:
    - Both modes:
      - force 100 rows per page
      - count visible rows
      - scan through visible rows (top -> bottom)
    - Dry-run:
      - produce audit rows only (no clicks)
    - Actual:
      - archive using the original click flow
      - reload list and re-apply 100 rows each time (DOM changes)
    """

    logs: List[Dict] = []
    rows_out: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("BulkArchive", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    driver, wait = get_driver(config)

    # Normalise excluded IDs
    excluded_set = {str(x).strip() for x in excluded_ids if str(x).strip()}
    log(f"Excluded IDs: {', '.join(sorted(excluded_set)) or '(none)'}")

    processed = 0

    try:
        # ========== Load list once initially ==========
        driver.get(lams_course_mgmt_url)
        driver.get(lams_course_mgmt_url)
        _set_rows_per_page(wait, log, "100")
        _click_sort_twice(wait, log)

        # Count visible rows
        total_rows = _get_visible_row_count(driver, log)
        log(f"Detected {total_rows} rows currently visible in table.", "info")

        if total_rows == 0:
            log("No rows detected. Are you on the correct Org Manage page and logged in?", "error")
            return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

        # ===============================
        # DRY-RUN MODE: scan table once
        # ===============================
        if dry_run:
            scanned = 0
            for i in range(1, total_rows + 1):

                # Stop / Pause checkpoint
                if stop_flag():
                    log("Stop requested during DRY-RUN.", "warn")
                    break

                if pause_flag():
                    log("Paused by user (DRY-RUN).", "info")
                    while pause_flag():
                        time.sleep(0.4)
                        if stop_flag():
                            log("Stop requested while paused (DRY-RUN).", "warn")
                            return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

                if scanned >= max_courses:
                    log("Reached max_courses safety cap (DRY-RUN).", "info")
                    break

                try:
                    cid = wait.until(EC.presence_of_element_located((By.XPATH, ID_CELL_XPATH.format(i=i)))).text.strip()
                    cname = wait.until(EC.presence_of_element_located((By.XPATH, NAME_LINK_XPATH.format(i=i)))).text.strip()

                    if cid in excluded_set:
                        log(f"Skipped excluded: {cid} – {cname}", "info")
                        continue

                    scanned += 1
                    processed += 1
                    progress_callback(processed, max_courses)

                    log(f"[DRY-RUN] Would archive {cid} – {cname}", "warn")
                    rows_out.append({"course_id": cid, "course_name": cname, "action": "DRY-RUN"})

                except StaleElementReferenceException:
                    log("Stale element during DRY-RUN scan. Reloading and continuing.", "warn")
                    driver.get(lams_course_mgmt_url)
                    _set_rows_per_page(wait, log, "100")
                    _click_sort_twice(wait, log)
                    total_rows = _get_visible_row_count(driver, log)
                    continue

                except TimeoutException:
                    # Skip if a particular row can't be read
                    log(f"Timeout reading row {i}. Skipping.", "warn")
                    continue

            log("DRY-RUN scan completed.", "info")
            return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

        # =====================================
        # ACTUAL MODE: archive row-by-row
        # =====================================
        # We use an index pointer and reload list after each archive.
        # Because archiving changes the table and row positions, we re-count total_rows each time.
        while processed < max_courses:

            # Stop / Pause checkpoint
            if stop_flag():
                log("Stop requested. Exiting safely.", "warn")
                break

            if pause_flag():
                log("Paused by user.", "info")
                while pause_flag():
                    time.sleep(0.4)
                    if stop_flag():
                        log("Stop requested while paused.", "warn")
                        return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

            # Always reload list and apply 100-per-page before selecting the next target
            driver.get(lams_course_mgmt_url)
            _set_rows_per_page(wait, log, "100")
            _click_sort_twice(wait, log)

            total_rows = _get_visible_row_count(driver, log)
            if total_rows == 0:
                log("No rows detected after reload. Stopping.", "warn")
                break

            found = False
            chosen_i: Optional[int] = None
            chosen_id = ""
            chosen_name = ""

            # Scan through all visible rows (up to 100)
            for i in range(1, total_rows + 1):
                try:
                    cid = wait.until(EC.presence_of_element_located((By.XPATH, ID_CELL_XPATH.format(i=i)))).text.strip()
                    cname = wait.until(EC.presence_of_element_located((By.XPATH, NAME_LINK_XPATH.format(i=i)))).text.strip()

                    if cid in excluded_set:
                        continue

                    chosen_i = i
                    chosen_id = cid
                    chosen_name = cname
                    found = True
                    break

                except (TimeoutException, StaleElementReferenceException):
                    continue

            if not found:
                log("No valid rows found to archive. Finished.", "info")
                break

            # One more stop checkpoint before destructive action
            if stop_flag():
                log("Stop requested before archiving.", "warn")
                break

            # ===== Archive flow (unchanged) =====
            try:
                driver.find_element(By.XPATH, NAME_LINK_XPATH.format(i=chosen_i)).click()

                wait.until(EC.element_to_be_clickable((By.XPATH, EDIT_XPATH))).click()
                wait.until(EC.presence_of_element_located((By.XPATH, STATUS_XPATH)))

                Select(driver.find_element(By.XPATH, STATUS_XPATH)).select_by_visible_text("Archived")
                wait.until(EC.element_to_be_clickable((By.XPATH, SAVE_XPATH))).click()

                processed += 1
                progress_callback(processed, max_courses)

                log(f"Archived: {chosen_id} – {chosen_name}", "info")
                rows_out.append({"course_id": chosen_id, "course_name": chosen_name, "action": "ARCHIVED"})

            except StaleElementReferenceException:
                log(f"Stale element while archiving {chosen_id}. Reloading list and retrying next.", "warn")
                continue

            except Exception as e:
                log(f"Failed to archive {chosen_id} – {chosen_name}: {e}", "error")
                rows_out.append({"course_id": chosen_id, "course_name": chosen_name, "action": f"ERROR: {e}"})
                # Continue to next item rather than killing the run
                continue

        log("Bulk archive run completed.", "info")
        return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

    except WebDriverException as e:
        log(f"WebDriver error: {e}", "error")
        return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

    except Exception as e:
        log(f"Fatal error: {e}", "error")
        return {"dataframe": pd.DataFrame(rows_out), "logs": logs}

    finally:
        # Only quit browser if STOP or fully finished
        if stop_flag() or processed >= max_courses:
            try:
                driver.quit()
                log("Closed Selenium driver.", "info")
            except Exception:
                pass
