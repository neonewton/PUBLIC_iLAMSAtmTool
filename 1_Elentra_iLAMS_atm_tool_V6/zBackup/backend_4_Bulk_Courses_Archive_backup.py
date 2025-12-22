import time
import pandas as pd
from typing import List, Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

from core.selenium_utils import (
    get_driver,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
)
from core.config import get_config


def run_bulk_course_archive(
    excluded_ids: List[str],
    dry_run: bool,
    max_courses: int,
    log_callback=default_log_callback,
    progress_callback=default_progress_callback,
    pause_flag=lambda: False,
    stop_flag=lambda: False,
) -> Dict:
    """
    Bulk archive iLAMS courses with Pause / Resume / Stop support.
    """

    logs: List[Dict] = []
    rows_out: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("BulkArchive", msg, level)
        logs.append(entry)
        log_callback(entry)

    # --- Setup ---
    config = get_config()
    driver, wait = get_driver(config)

    lams_course_mgmt_url = (
        "https://ilams.lamsinternational.com/lams/admin/orgmanage.do?org=1"
    )

    excluded_set = set(excluded_ids)
    processed = 0

    log(f"Excluded IDs: {', '.join(excluded_set) or '(none)'}")

    try:
        while True:

            # =========================
            # STOP / PAUSE CHECKPOINT
            # =========================
            if stop_flag():
                log("Stop requested. Exiting safely.", "warn")
                break

            if pause_flag():
                log("Paused by user.", "info")
                while pause_flag():
                    time.sleep(0.5)
                    if stop_flag():
                        log("Stop requested while paused.", "warn")
                        return {
                            "dataframe": pd.DataFrame(rows_out),
                            "logs": logs,
                        }

            if processed >= max_courses:
                log("Reached max_courses safety cap.")
                break

            try:
                # =========================
                # Load course list
                # =========================
                driver.get(lams_course_mgmt_url)
                driver.get(lams_course_mgmt_url)
                driver.get(lams_course_mgmt_url)

                # Set rows per page to 100
                rows_select_xpath = "/html/body/div/div/div/div/div[2]/div/table/tfoot/tr/th/select"

                rows_select = wait.until(
                    EC.presence_of_element_located((By.XPATH, rows_select_xpath))
                )

                Select(rows_select).select_by_visible_text("100")

                time.sleep(1)
                Select(rows_select).select_by_visible_text("100")

                # Then sort
                sort_xpath = '//*[@id="idsorter"]/div/div'

                sort_xpath = '//*[@id="idsorter"]/div/div'
                time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, sort_xpath))).click()
                time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, sort_xpath))).click()

                found_valid_row = False
                course_id = ""
                course_name = ""
                name_xpath = ""

                for row_index in range(1, 6):
                    id_xpath = f'//*[@id="content"]/div/div[2]/div/table/tbody/tr[{row_index}]/td[1]'
                    name_xpath_try = f'//*[@id="content"]/div/div[2]/div/table/tbody/tr[{row_index}]/td[2]/a'

                    try:
                        id_elem = wait.until(
                            EC.presence_of_element_located((By.XPATH, id_xpath))
                        )
                        candidate_id = id_elem.text.strip()

                        candidate_name = ""
                        for _ in range(2):
                            try:
                                name_elem = wait.until(
                                    EC.presence_of_element_located((By.XPATH, name_xpath_try))
                                )
                                candidate_name = name_elem.text.strip()
                                break
                            except StaleElementReferenceException:
                                time.sleep(0.5)

                        if candidate_id in excluded_set:
                            log(f"Skipped excluded: {candidate_id} – {candidate_name}")
                            continue

                        course_id = candidate_id
                        course_name = candidate_name
                        name_xpath = name_xpath_try
                        found_valid_row = True
                        break

                    except TimeoutException:
                        continue

                if not found_valid_row:
                    log("No valid rows found. Finished.")
                    break

                processed += 1
                progress_callback(processed, max_courses)

                if dry_run:
                    log(f"[DRY-RUN] Would archive {course_id} – {course_name}", "warn")
                    rows_out.append(
                        {
                            "course_id": course_id,
                            "course_name": course_name,
                            "action": "DRY-RUN",
                        }
                    )

                    excluded_set.add(course_id)   # ⭐ KEY LINE
                    continue


                if stop_flag():
                    log("Stop requested before archiving.", "warn")
                    break

                driver.find_element(By.XPATH, name_xpath).click()

                edit_xpath = '//*[@id="editCourse"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, edit_xpath))).click()

                status_xpath = '//*[@id="stateId"]'
                wait.until(EC.presence_of_element_located((By.XPATH, status_xpath)))

                select = Select(driver.find_element(By.XPATH, status_xpath))
                select.select_by_visible_text("Archived")

                save_xpath = '//*[@id="saveButton"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath))).click()

                log(f"Archived: {course_id} – {course_name}")

                rows_out.append(
                    {
                        "course_id": course_id,
                        "course_name": course_name,
                        "action": "ARCHIVED",
                    }
                )

            except StaleElementReferenceException:
                log("Stale element detected. Reloading page.", "warn")
                time.sleep(1)
                continue

    except Exception as e:
        log(f"Fatal error: {e}", "error")


    finally:
        # Only quit browser if STOP or fully finished
        if stop_flag() or processed >= max_courses:
            try:
                driver.quit()
                log("Closed Selenium driver.", "info")
            except Exception:
                pass

    return {
        "dataframe": pd.DataFrame(rows_out),
        "logs": logs,
    }
