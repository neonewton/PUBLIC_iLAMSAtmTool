# core/elentra_link_upload.py

from typing import Dict, List

from selenium.webdriver.common.by import By

from .config import SeleniumConfig, get_config
from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
    get_driver,
    wait_and_click,
    wait_and_type,
)


# TODO: update these selectors to match your Elentra Event form
ADMIN_URL_LOCATOR = (By.NAME, "admin_url")      # example only
STAFF_URL_LOCATOR = (By.NAME, "staff_url")      # example only
STUDENT_URL_LOCATOR = (By.NAME, "student_url")  # example only
MONITOR_URL_LOCATOR = (By.NAME, "monitor_url")  # example only
SAVE_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button[type='submit']")  # example only


def _build_lams_urls(config: SeleniumConfig, lesson_id: str) -> Dict[str, str]:
    """
    Build the 4 URLs for Admin/Staff/Student/Monitor given a base LAMS URL + lesson_id.
    Adjust patterns to match your environment.
    """
    base = config.lams_base_url or ""
    lesson_id = lesson_id.strip()

    # Example pattern – REPLACE with your actual LAMS URL patterns
    admin_url = f"{base}/monitoring/monitorLesson.do?lessonID={lesson_id}"
    staff_url = f"{base}/teacher/lesson.do?lessonID={lesson_id}"
    student_url = f"{base}/learning/learner.do?lessonID={lesson_id}"
    monitor_url = f"{base}/monitoring/monitorLesson.do?lessonID={lesson_id}&role=monitor"

    return {
        "admin": admin_url,
        "staff": staff_url,
        "student": student_url,
        "monitor": monitor_url,
    }


def run_elentra_link_upload(
    event_id: str,
    lams_lesson_id: str,
    upload_admin: bool,
    upload_staff: bool,
    upload_student: bool,
    upload_monitor: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> List[Dict]:
    """
    High-level workflow:
    - Attach to existing Chrome session
    - Navigate to Elentra Event edit page
    - Fill in selected URL fields
    - Save form
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ElentraUpload", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    total_steps = 6
    step = 0

    event_id = event_id.strip()
    lesson_id = lams_lesson_id.strip()

    if not config.elentra_base_url:
        log("Elentra base URL is not configured. Set it in Home page.", "error")
        return logs

    if not event_id:
        log("Empty Event ID provided.", "error")
        return logs

    urls = _build_lams_urls(config, lesson_id)
    log(f"Generated LAMS URLs for lesson {lesson_id}.", "info")

    try:
        driver, wait = get_driver(config)
        step += 1
        progress_callback(step, total_steps)
        log("Attached to Selenium driver.", "info")

        # TODO: Update this pattern to your actual event edit URL
        event_edit_url = f"{config.elentra_base_url}/events/{event_id}/edit"
        driver.get(event_edit_url)
        step += 1
        progress_callback(step, total_steps)
        log(f"Opened Elentra Event edit page: {event_edit_url}", "info")

        # Fill each selected URL field
        if upload_admin:
            wait_and_type(wait, ADMIN_URL_LOCATOR, urls["admin"], "Admin URL", log_callback=log_callback)
        if upload_staff:
            wait_and_type(wait, STAFF_URL_LOCATOR, urls["staff"], "Staff URL", log_callback=log_callback)
        if upload_student:
            wait_and_type(wait, STUDENT_URL_LOCATOR, urls["student"], "Student URL", log_callback=log_callback)
        if upload_monitor:
            wait_and_type(wait, MONITOR_URL_LOCATOR, urls["monitor"], "Monitor URL", log_callback=log_callback)

        step += 1
        progress_callback(step, total_steps)
        log("Updated selected link fields.", "info")

        # Save / submit form
        wait_and_click(wait, SAVE_BUTTON_LOCATOR, "Save button", log_callback=log_callback)
        step += 1
        progress_callback(step, total_steps)
        log("Submitted Event form.", "info")

        # Optionally: wait for some confirmation element / message
        # ...

        step += 1
        progress_callback(step, total_steps)
        log("Elentra link upload completed successfully.", "info")

        driver.quit()
        step += 1
        progress_callback(step, total_steps)
        log("Closed Selenium driver.", "info")

    except Exception as e:
        log(f"Elentra link upload failed: {e}", "error")

    return logs
