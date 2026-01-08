# core/elentra_link_upload.py


import re
from typing import Dict, List, Union, IO, Callable
import time
import random
import pandas as pd
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)


import streamlit as st

from .config import SeleniumConfig, get_config
from .selenium_utils import (
    LogCallback,
    ProgressCallback,
    make_log_entry,
    default_log_callback,
    default_progress_callback,
    get_driver,
    wait_and_click,
    dramatic_input,
    highlight,
    time_sleep,
    time_out,
    click_text
)

# core/bulk_search_users.py

SEARCH_INPUT_LOCATOR = (By.NAME, "searchString")           # example only
SEARCH_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button[type='submit']")  # example only
RESULT_ROWS_LOCATOR = (By.CSS_SELECTOR, "table.search-results tbody tr")  # example only
RESULT_COLS_LOCATOR = (By.CSS_SELECTOR, "td")  # example only


TIMESLEEP = 1.5

# === iLAMS XPATHS (PROVEN) ===
SEARCH_INPUT_XPATH = "/html/body/div[1]/div/main/div[1]/div[2]/input"
RESULT_ROWS_XPATH = "/html/body/div[1]/div/main/table/tbody/tr"
lams_url = r"https://ilams.lamsinternational.com/lams/admin/usersearch.do"

TIMESLEEP = 1.5

def go_user_search_page(
    log_callback: Callable = lambda x: None,
    progress_callback: Callable = lambda c, t: None,
) -> dict:

    logs = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("iLAMS User Search", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()

    try:
        driver, wait = get_driver(config)
        log("Attached to Chrome via remote debugging.")
    except Exception as e:
        log(f"Failed to attach to Chrome: {e}", "error")
        return {"logs": logs}

    try:
        driver.get("https://ilams.lamsinternational.com/lams/admin/usersearch.do")
        time.sleep(2)
        log("Opened iLAMS User Search page.")
    finally:
        pass

    return {"logs": logs}


def run_user_search(
    search_values: List[str],
    log_callback: Callable = lambda x: None,
    progress_callback: Callable = lambda c, t: None,
    stop_flag: Callable[[], bool] = lambda: False,
) -> Dict:

    logs = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("iLAMS User Search", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()

    try:
        driver, wait = get_driver(config)
        log("Attached to Chrome via remote debugging.")
    except Exception as e:
        log(f"Failed to attach to Chrome: {e}", "error")
        return {"dataframe": pd.DataFrame(), "logs": logs}

    def safe_text(xpath: str) -> str:
        try:
            return driver.find_element(By.XPATH, xpath).text.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            return ""

    def ensure_page(retries: int = 3):
        for attempt in range(retries + 1):
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT_XPATH)))
                return
            except TimeoutException:
                if attempt < retries:
                    driver.get(lams_url)
                    time.sleep(1.5)
                    driver.get(lams_url)
                    time.sleep(1.5)
                else:
                    raise

    results = []
    total = max(len(search_values), 1)

    for idx, raw_input in enumerate(search_values, start=1):

        # STOP checkpoint
        if stop_flag():
            log("Stop requested by user. Exiting safely.", "warn")
            break


        progress_callback(idx, total)

        original_input = raw_input.strip()
        if not original_input:
            continue

        # If name contains brackets, strip (Private), (TTSH), etc.
        search_term = re.sub(r"\s*\(.*?\)", "", original_input)

        try:
            ensure_page()

            box = wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT_XPATH)))
            box.clear()
            time.sleep(0.1)
            box.send_keys(search_term)
            box.send_keys(Keys.RETURN)
            time.sleep(TIMESLEEP)

            rows = driver.find_elements(By.XPATH, RESULT_ROWS_XPATH)

            # 🔹 CASE 1: No results found
            if not rows:
                results.append({
                    "Input": original_input,
                    "Row #": "",                      # or 0 if you prefer numeric
                    "DL check account?": "Acc Not Found",
                    "User ID": "",
                    "Login": "",
                    "First Name": "",
                    "Last Name": "",
                })

                log(f"[{idx}/{total}] {original_input} → Acc Not Found")
                continue   # 🔴 IMPORTANT: skip row parsing below

            # 🔹 CASE 2: One or more results
            status = "Acc >1" if len(rows) > 1 else "Exist"

            for idx_row, row_el in enumerate(rows, start=1):
                cols = row_el.find_elements(By.TAG_NAME, "td")
                texts = [c.text.strip() for c in cols]

                results.append({
                    "Input": original_input,          # always original input
                    "Row #": idx_row,                 # 1, 2, 3, ...
                    "DL check account?": status,
                    "User ID": texts[0] if len(texts) > 0 else "",
                    "Login": texts[1] if len(texts) > 1 else "",
                    "First Name": texts[2] if len(texts) > 2 else "",
                    "Last Name": texts[3] if len(texts) > 3 else "",
                })

            log(f"[{idx}/{total}] {original_input} → {status}")


        except Exception as e:
            log(f"[{idx}/{total}] Error processing '{original_input}': {e}", "error")
            results.append({
                "Input": original_input,
                "DL check account?": "ERROR",
                "User ID": "",
                "Login": "",
                "First Name": "",
                "Last Name": "",
                "Row": "ERROR",
            })

        time.sleep(random.uniform(1, 2))

    df = pd.DataFrame(results)
    log("User search completed successfully.")
    return {"dataframe": df, "logs": logs}

