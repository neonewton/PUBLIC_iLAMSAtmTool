# core/bulk_course_archive.py

from typing import List, Dict
import pandas as pd

from selenium.webdriver.common.by import By

from .config import get_config
from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
    get_driver,
)


# TODO: Adjust these for your LAMS org manage page
ORG_MANAGE_URL_SUFFIX = "/orgmanage/courses"  # example

COURSE_ROW_LOCATOR = (By.CSS_SELECTOR, "table.courses-table tbody tr")  # example
COURSE_COL_LOCATOR = (By.CSS_SELECTOR, "td")
EDIT_LINK_LOCATOR = (By.CSS_SELECTOR, "a.edit-course")  # inside the row (example)

STATUS_SELECT_LOCATOR = (By.NAME, "courseStatus")  # example
SAVE_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button[type='submit']")  # example


def run_bulk_course_archive(
    excluded_ids: List[str],
    dry_run: bool,
    max_courses: int,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    High-level flow:
    - Open org manage courses page
    - Iterate course rows, build candidate list
    - For each candidate (not excluded, within max), set status to Archived (unless dry-run)
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("BulkArchive", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    if not config.lams_base_url:
        log("LAMS base URL is not configured. Set it in Home page.", "error")
        return {"dataframe": pd.DataFrame(), "logs": logs}

    excluded_set = {eid.strip() for eid in excluded_ids if eid.strip()}
    log(f"Excluded IDs: {', '.join(sorted(excluded_set)) or '(none)'}", "info")

    org_courses_url = f"{config.lams_base_url}{ORG_MANAGE_URL_SUFFIX}"

    from selenium.webdriver.support import expected_conditions as EC

    try:
        driver, wait = get_driver(config)
        log("Attached to Selenium driver.", "info")
    except Exception as e:
        log(f"Failed to start driver: {e}", "error")
        return {"dataframe": pd.DataFrame(), "logs": logs}

    candidates = []

    try:
        driver.get(org_courses_url)
        log(f"Opened Org Manage Courses page: {org_courses_url}", "info")

        rows = wait.until(EC.presence_of_all_elements_located(COURSE_ROW_LOCATOR))

        for row in rows:
            cols = row.find_elements(*COURSE_COL_LOCATOR)
            texts = [c.text.strip() for c in cols]
            if not texts:
                continue

            # TODO: Decide which column holds the course ID
            course_id = texts[0]  # example: first column is ID
            course_name = texts[1] if len(texts) > 1 else ""
            status = texts[2] if len(texts) > 2 else ""

            candidates.append(
                {
                    "course_id": course_id,
                    "course_name": course_name,
                    "status": status,
                    "row_element": row,
                }
            )

        log(f"Found {len(candidates)} courses on page.", "info")

    except Exception as e:
        log(f"Error loading or parsing courses: {e}", "error")
        try:
            driver.quit()
        except Exception:
            pass
        return {"dataframe": pd.DataFrame(), "logs": logs}

    # Now process candidates
    processed_rows = []
    count = 0
    total = min(len(candidates), max_courses)

    for idx, course in enumerate(candidates, start=1):
        if count >= max_courses:
            break

        progress_callback(idx, total)

        cid = course["course_id"]
        cname = course["course_name"]
        status = course["status"]

        if cid in excluded_set:
            log(f"Skipping excluded course: {cid} – {cname}", "info")
            continue

        count += 1

        if dry_run:
            log(f"[DRY-RUN] Would archive: {cid} – {cname} (current status: {status})", "warn")
            processed_rows.append(
                {
                    "course_id": cid,
                    "course_name": cname,
                    "previous_status": status,
                    "action": "DRY-RUN",
                }
            )
            continue

        try:
            # Click Edit in row
            edit_link = course["row_element"].find_element(*EDIT_LINK_LOCATOR)
            edit_link.click()
            log(f"Opened edit page for course {cid} – {cname}", "info")

            # Change status to Archived
            status_select = wait.until(EC.visibility_of_element_located(STATUS_SELECT_LOCATOR))
            from selenium.webdriver.support.ui import Select

            select = Select(status_select)
            select.select_by_visible_text("Archived")  # adjust to exact label
            log(f"Set status to 'Archived' for course {cid}.", "info")

            # Save
            save_btn = wait.until(EC.element_to_be_clickable(SAVE_BUTTON_LOCATOR))
            save_btn.click()
            log(f"Saved course {cid}.", "info")

            processed_rows.append(
                {
                    "course_id": cid,
                    "course_name": cname,
                    "previous_status": status,
                    "action": "ARCHIVED",
                }
            )

            # Go back to course list page for next iteration
            driver.get(org_courses_url)
            rows = wait.until(EC.presence_of_all_elements_located(COURSE_ROW_LOCATOR))

            # Re-bind row elements because page reloaded
            # (Simplest: just ignore row_element and rely on next loop indexes.)

        except Exception as e:
            log(f"Failed to archive course {cid} – {cname}: {e}", "error")
            processed_rows.append(
                {
                    "course_id": cid,
                    "course_name": cname,
                    "previous_status": status,
                    "action": f"ERROR: {e}",
                }
            )

    try:
        driver.quit()
        log("Closed Selenium driver.", "info")
    except Exception as e:
        log(f"Error closing driver: {e}", "warn")

    df = pd.DataFrame(processed_rows)
    log("Bulk course archive completed.", "info")
    return {"dataframe": df, "logs": logs}
