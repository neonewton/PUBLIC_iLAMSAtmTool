# core/search_users.py

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


# TODO: adjust these locators to match your iLAMS usersearch.do page
SEARCH_INPUT_LOCATOR = (By.NAME, "searchString")           # example only
SEARCH_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button[type='submit']")  # example only
RESULT_ROWS_LOCATOR = (By.CSS_SELECTOR, "table.search-results tbody tr")  # example only
RESULT_COLS_LOCATOR = (By.CSS_SELECTOR, "td")  # example only


def run_user_search(
    search_values: List[str],
    include_second_row: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    For each search value:
    - Loads iLAMS usersearch page
    - Submits search
    - Parses up to 2 result rows
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("SearchUsers", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    if not config.lams_base_url:
        log("LAMS base URL is not configured. Set it in Home page.", "error")
        return {"dataframe": pd.DataFrame(), "logs": logs}

    # TODO: adjust to your actual user search URL
    usersearch_url = f"{config.lams_base_url}/usersearch.do"

    try:
        driver, wait = get_driver(config)
        log("Attached to Selenium driver.", "info")
    except Exception as e:
        log(f"Failed to start driver: {e}", "error")
        return {"dataframe": pd.DataFrame(), "logs": logs}

    records = []
    total = max(len(search_values), 1)

    from selenium.webdriver.support import expected_conditions as EC

    for i, value in enumerate(search_values, start=1):
        value = str(value).strip()
        progress_callback(i, total)
        if not value:
            continue

        try:
            driver.get(usersearch_url)
            log(f"[{i}/{total}] Opened usersearch for value: {value}", "info")

            # Type and submit search
            input_el = wait.until(EC.visibility_of_element_located(SEARCH_INPUT_LOCATOR))
            input_el.clear()
            input_el.send_keys(value)

            btn = wait.until(EC.element_to_be_clickable(SEARCH_BUTTON_LOCATOR))
            btn.click()
            log(f"[{i}/{total}] Submitted search for: {value}", "info")

            # Get result rows
            rows = wait.until(EC.presence_of_all_elements_located(RESULT_ROWS_LOCATOR))
            if not rows:
                log(f"[{i}/{total}] No results for: {value}", "warn")
                continue

            def extract_row(row_el, row_label: str):
                cols = row_el.find_elements(*RESULT_COLS_LOCATOR)
                texts = [c.text.strip() for c in cols]
                records.append(
                    {
                        "Input": value,
                        "RowLabel": row_label,
                        "Col1": texts[0] if len(texts) > 0 else "",
                        "Col2": texts[1] if len(texts) > 1 else "",
                        "Col3": texts[2] if len(texts) > 2 else "",
                        "Col4": texts[3] if len(texts) > 3 else "",
                        "RawColumns": " | ".join(texts),
                    }
                )

            # Always take first row
            extract_row(rows[0], "Row1")
            log(f"[{i}/{total}] Captured Row1 for: {value}", "info")

            # Optionally take second row
            if include_second_row and len(rows) > 1:
                extract_row(rows[1], "Row2")
                log(f"[{i}/{total}] Captured Row2 for: {value}", "info")

        except Exception as e:
            log(f"[{i}/{total}] Error while searching '{value}': {e}", "error")

    try:
        driver.quit()
        log("Closed Selenium driver.", "info")
    except Exception as e:
        log(f"Error closing driver: {e}", "warn")

    df = pd.DataFrame(records)
    log("User search completed.", "info")
    return {"dataframe": df, "logs": logs}
