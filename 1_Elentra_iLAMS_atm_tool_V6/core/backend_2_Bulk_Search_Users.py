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
TABLE_ROW1_XPATHS = [f"/html/body/div[1]/div/main/table/tbody/tr[1]/td[{i}]" for i in range(1, 6)]
TABLE_ROW2_XPATHS = [f"/html/body/div[1]/div/main/table/tbody/tr[2]/td[{i}]" for i in range(1, 6)]

TIMESLEEP = 1.5


def run_user_search(
    search_values: List[str],
    include_second_row: bool = True,
    log_callback: Callable = lambda x: None,
    progress_callback: Callable = lambda c, t: None,
) -> Dict:
    logs = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("iLAMS User Search", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    lams_url = r"https://ilams.lamsinternational.com/lams/admin/usersearch.do"

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
                    driver.get(lams_url)
                    time.sleep(1.5)
                else:
                    raise

    results = []
    total = max(len(search_values), 1)

    for idx, raw_input in enumerate(search_values, start=1):
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
            time.sleep(0.2)
            box.send_keys(search_term)
            box.send_keys(Keys.RETURN)
            time.sleep(TIMESLEEP)

            row1 = [safe_text(xp) for xp in TABLE_ROW1_XPATHS]
            row2 = [safe_text(xp) for xp in TABLE_ROW2_XPATHS]

            if any(row1) and any(row2):
                status = "Acc >1"
            elif any(row1):
                status = "Exist"
            else:
                status = "Acc Not Found"

            def clean_email(email: str) -> str:
                return "" if "@e.ntu.edu.sg" in email.lower() else email

            email1 = clean_email(row1[4]) if len(row1) > 4 else ""
            email2 = clean_email(row2[4]) if len(row2) > 4 else ""

            results.append({
                "Input": original_input,
                "DL check account?": status,
                "iLAMS email address": email1,
                "User ID": row1[0],
                "Login": row1[1],
                "First Name": row1[2],
                "Last Name": row1[3],
                "Row": "Row1",
            })

            if include_second_row and status == "Acc >1":
                results.append({
                    "Input": f"{original_input} (Row2)",
                    "DL check account?": status,
                    "iLAMS email address": email2,
                    "User ID": row2[0],
                    "Login": row2[1],
                    "First Name": row2[2],
                    "Last Name": row2[3],
                    "Row": "Row2",
                })

            log(f"[{idx}/{total}] {original_input} → {status}")

        except Exception as e:
            log(f"[{idx}/{total}] Error processing '{original_input}': {e}", "error")
            results.append({
                "Input": original_input,
                "DL check account?": "ERROR",
                "iLAMS email address": "",
                "User ID": "",
                "Login": "",
                "First Name": "",
                "Last Name": "",
                "Row": "ERROR",
            })

        time.sleep(random.uniform(0.8, 1.6))

    df = pd.DataFrame(results)
    log("User search completed successfully.")
    return {"dataframe": df, "logs": logs}

