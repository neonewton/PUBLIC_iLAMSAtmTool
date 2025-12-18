# core/elentra_link_upload.py


import re
from typing import Dict, List, Union, IO
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

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


def run_elentra_link_upload(
    lams_lesson_title: str,
    elentra_event_id: str,
    lams_lesson_id: str,
    upload_student: bool,
    upload_monitor: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,

) -> List[Dict]:
    start_time = time.time() 
    lams_lesson_title = lams_lesson_title
    elentra_event_url   = f"https://ntu.elentra.cloud/events?id={elentra_event_id}"
    lams_monitor_title = f"LAMS {lams_lesson_title} (Facilitator/CE)"
    lams_monitor_url   = f"https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID={lams_lesson_id}"
    lams_student_title = f"LAMS {lams_lesson_title}"
    lams_student_url   = f"https://ilams.lamsinternational.com/lams/home/learner.do?lessonID={lams_lesson_id}"

    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ElentraUpload", msg, level)
        logs.append(entry)
        log_callback(entry)

    config = get_config()
    total_steps = 6
    step = 0

    def should_stop():
        return st.session_state.get("stop_requested", False)

    if not config.elentra_base_url:
        log("Elentra base URL is not configured. Set it in Home page.", "error")
        return logs

    if not elentra_event_id:
        log("Empty Event ID provided.", "error")
        return logs

    try:
        # ----------------------------------------------
        # STEP 1: Attach to Selenium
        # ----------------------------------------------
        driver, wait = get_driver(config)
        step += 1
        progress_callback(step, total_steps)
        log("Attached to Selenium driver.")

        # ----------------------------------------------
        # STEP 2: Open Elentra Event Page (Twice)
        # ----------------------------------------------
        driver.get(elentra_event_url)
        log("Navigated to Elentra event page (1st load).")
        driver.get(elentra_event_url)
        log("Navigated to Elentra event page (2nd load).")
        time.sleep(time_sleep)

        # ----------------------------------------------
        # STEP 3: Click Admin > Content tabs
        # ----------------------------------------------
        # wait_and_click(driver, "//a[contains(text(), 'Administrator View')]", timeout=time_out, highlight_fn=highlight, 
        #             message="Administrator View clicked",sleep_after=time_sleep)
        
        # wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[2]/ul/li[2]/a", timeout=time_out, highlight_fn=highlight,
        #             message="Content tab clicked", sleep_after=time_sleep)

        click_text(driver, "Administrator View")

        click_text(driver, "Content")


        # ----------------------------------------------
        # STEP 4: Read Event Name
        # ----------------------------------------------
        h1 = WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div/h1[1]"))
        )
        highlight(h1)
        elentra_event_name = h1.text
        log(f"Page title detected: {elentra_event_name}")

        # ----------------------------------------------
        # STEP 5: MONITOR RESOURCE WORKFLOW
        # ----------------------------------------------
        if upload_monitor:
            # Stop if requested
            log("⏳ Inserting MONITOR URL...")

            if should_stop():
                log("🛑 Stop requested — stopping before navigation.")
                try:
                    driver.quit()
                except:
                    pass
                return logs

            # scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            log("Scrolled to bottom.")
            time.sleep(time_sleep)

            # Add a Resource
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/div[1]/a",
                        timeout=time_out, highlight_fn=highlight,
                        message="Add a Resource clicked", sleep_after=time_sleep)

            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div/label[6]",
                        timeout=time_out, highlight_fn=highlight,
                        message="Link option selected", sleep_after=time_sleep)

            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]",
                        timeout=time_out, highlight_fn=highlight,
                        message="Next clicked", sleep_after=time_sleep)

            # Optional / No timeframe / Next
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]", timeout=time_out,
                        highlight_fn=highlight, message="Optional selected", sleep_after=time_sleep)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/label[4]", timeout=time_out,
                        highlight_fn=highlight, message="No timeframe selected", sleep_after=time_sleep)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", timeout=time_out,
                        highlight_fn=highlight, message="Next clicked", sleep_after=time_sleep)

            # Accessibility, hidden, published
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]", timeout=time_out,
                        highlight_fn=highlight, message="Accessible Anytime selected", sleep_after=time_sleep)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[2]", timeout=time_out,
                        highlight_fn=highlight, message="Hide this resource", sleep_after=time_sleep)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[4]/label[1]", timeout=time_out,
                        highlight_fn=highlight, message="Published selected", sleep_after=time_sleep)

            # Next step (final)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", timeout=time_out,
                        highlight_fn=highlight, message="Final Next clicked", sleep_after=time_sleep)

            # Proxy not required
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/div/label[1]", timeout=time_out,
                        highlight_fn=highlight, message="Proxy disabled", sleep_after=time_sleep)

            # Fill URL
            el = WebDriverWait(driver, time_out).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/div/input"))
            )
            highlight(el)
            el.clear()
            el.send_keys(lams_monitor_url)
            log("Monitor URL entered.")

            # Title
            el = WebDriverWait(driver, time_out).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/div/input"))
            )
            highlight(el)
            el.clear()
            el.send_keys(lams_monitor_title)
            log("Monitor title entered.")

            # Scroll modal
            modal = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.ID, "event-resource-modal"))
            )
            highlight(modal)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal)

            # Description iframe
            iframe = driver.find_element(
                By.CSS_SELECTOR,
                "#cke_event-resource-link-description iframe.cke_wysiwyg_frame"
            )
            driver.switch_to.frame(iframe)
            editor_body = driver.find_element(By.CSS_SELECTOR, "body[contenteditable='true']")
            highlight(editor_body)
            editor_body.clear()
            editor_body.send_keys(lams_monitor_title)
            driver.switch_to.default_content()
            log("Monitor description entered.")

            # Save + Close
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", timeout=time_out,
                        highlight_fn=highlight, message="Monitor resource saved", sleep_after=time_sleep)
            wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]", timeout=time_out,
                        highlight_fn=highlight, message="Monitor resource dialog closed", sleep_after=time_sleep)

        # ----------------------------------------------
        # STEP 6: STUDENT RESOURCE WORKFLOW
        # ----------------------------------------------
        if upload_student:
            # Stop if requested
            log("⏳ Inserting STUDENT URL...")

            if should_stop():
                log("🛑 Stop requested — stopping before navigation.")
                try:
                    driver.quit()
                except:
                    pass
                return logs

            if True: #to group the lines of code
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(time_sleep)
            
            # 9) Add a Resource
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/div[1]/a", timeout=time_out, highlight_fn=highlight,
                message="Add a Resource link clicked", sleep_after=time_sleep)
            # 10) 'Link' Resource checkbox
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div/label[6]", timeout=time_out, highlight_fn=highlight,
                message="Link checkbox selected", sleep_after=time_sleep)

            # 11) Next Step
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Next Step Button clicked", sleep_after=time_sleep
            )

            # 12) Required
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[2]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Optional selected", sleep_after=time_sleep
            )

            # 13) No Timeframe
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/label[4]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ No Timeframe link clicked", sleep_after=time_sleep
            )

            # 14) Next Step
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Next step (to Hide)", sleep_after=time_sleep
            )

            # 15) No, this resource is accessible any time
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ No, this resource is accessible any time selected", sleep_after=time_sleep
            )

            # 16) Hide this resource from learners
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[1]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Allow learners to view this resource selected", sleep_after=time_sleep
            )

            # 17) Published
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[4]/label[1]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Published selected", sleep_after=time_sleep
            )

            # 18) Next Step
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Final Next Step clicked", sleep_after=time_sleep
            )

            # 18.5) No, the proxy isn’t required to be enabled
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/div/label[1]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ No, the proxy isnt required to be enabled selected", sleep_after=time_sleep
            )

            print("⏳ Inserting LAMS title & URL now ⏳")
            log("⏳ Inserting LAMS title & URL now ⏳")

            # 19) Enter Student URL
            time.sleep(0.5)
            el = WebDriverWait(driver, time_sleep).until(
                EC.visibility_of_element_located((By.XPATH,
                    "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/div/input"
                ))
            )
            highlight(el)
            el.clear()
            el.send_keys(lams_student_url)
            print("✅ Monitor URL entered")
            log("✅ Monitor URL entered")
            time.sleep(time_sleep)

            # 20) Enter Lesson Title
            el = WebDriverWait(driver, time_sleep).until(
                EC.visibility_of_element_located((By.XPATH,
                    "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/div/input"
                ))
            )
            highlight(el)
            el.clear()
            el.send_keys(lams_student_title)
            print("✅ Title entered")
            time.sleep(time_sleep)

            # 21) Scroll the message box to the bottom
            modal = WebDriverWait(driver, time_out).until(
                EC.presence_of_element_located((By.ID, "event-resource-modal"))
            )
            highlight(modal)
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal)
            print("✅ Modal scrolled to bottom")
            log("✅ Modal scrolled to bottom")
            time.sleep(time_sleep)
            time.sleep(0.5)

            # 22) Enter Description
            time.sleep(0.5)
            iframe = driver.find_element(
                By.CSS_SELECTOR,
                "#cke_event-resource-link-description iframe.cke_wysiwyg_frame"
            )
            driver.switch_to.frame(iframe)
            print("✅ Switched to iframe")
            log("✅ Switched to iframe")

            editor_body = driver.find_element(
                By.CSS_SELECTOR,
                "body[contenteditable='true']"
            )
            highlight(editor_body)
            try:
                editor_body.clear()
            except Exception:
                editor_body.send_keys(Keys.COMMAND + "a", Keys.DELETE)

            editor_body.send_keys(lams_student_title)
            driver.switch_to.default_content()
            print("✅ Description added")
            log("✅ Description added")
            time.sleep(time_sleep)

            # 23) Save Resource
            time.sleep(0.5)
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Resource saved", sleep_after=time_sleep
            )

            # 24) Close
            time.sleep(0.5)
            wait_and_click(
                driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]",
                timeout=time_out, highlight_fn=highlight,
                message="✅ Closed attachment dialog", sleep_after=time_sleep
            )


        # ----------------------------------------------
        # STEP 7: Final Summary
        # ----------------------------------------------
        log("🎉 Resource added successfully.")
        log(f"Elentra Event Name: {elentra_event_name}")
        log(f"LAMS Lesson ID: {lams_lesson_id}")

        if upload_monitor:
            log(f"Monitor Title: {lams_monitor_title}")
            log(f"Monitor URL: {lams_monitor_url}")

        if upload_student:
            log(f"Student Title: {lams_student_title}")
            log(f"Student URL: {lams_student_url}")

    except Exception as e:
        log(f"❌ Resource not added successfully: {e}")

    finally:
        elapsed = time.time() - start_time
        log(f"⏱ Total elapsed time: {elapsed:.1f} seconds")
        try:
            driver.quit()
        except:
            pass
    return logs


"""Generation Excels Module"""


EMAIL_REGEX = re.compile(r"([a-zA-Z0-9_.+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z0-9\-]+)")


def _parse_line_to_record(line: str) -> Dict:
    """
    Attempt to parse an input line into:
    - First Name
    - Last Name
    - Email
    - Username
    - Raw
    """
    raw = line.strip()

    # Extract email
    email_match = EMAIL_REGEX.search(raw)
    email = email_match.group(1) if email_match else ""

    # Extract name part = raw with email removed
    name_part = raw.replace(email, "").replace("<", "").replace(">", "").strip(" -\t")

    first_name = ""
    last_name = ""
    username = ""

    if email:
        username = email.split("@")[0]
        # Derive name from username if no explicit name
        if not name_part:
            # try split by ., _, or -
            parts = re.split(r"[._\-]+", username)
            if len(parts) >= 2:
                first_name = parts[0].title()
                last_name = " ".join(p.title() for p in parts[1:])
            else:
                first_name = username.title()
                last_name = ""
        else:
            # Name provided: split into first + last
            parts = name_part.split()
            if len(parts) == 1:
                first_name = parts[0].title()
                last_name = ""
            else:
                first_name = parts[0].title()
                last_name = " ".join(p.title() for p in parts[1:])
    else:
        # No email found, put everything into RawName
        name_part = raw
        parts = name_part.split()
        if parts:
            first_name = parts[0].title()
            if len(parts) > 1:
                last_name = " ".join(p.title() for p in parts[1:])

    return {
        "RawInput": raw,
        "FirstName": first_name,
        "LastName": last_name,
        "Email": email,
        "Username": username,
    }


def generate_user_excel(
    raw_text: str,
    mode: str,
    course_name: str,
    output_path: str,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    Parse raw text input into a table for user creation.
    mode: "student" or "staff"
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ExcelGeneration", msg, level)
        logs.append(entry)
        log_callback(entry)

    lines = [l for l in (raw_text or "").splitlines() if l.strip()]
    if not lines:
        log("No lines found in input text.", "warn")
        df = pd.DataFrame(columns=["RawInput", "FirstName", "LastName", "Email", "Username"])
        return {
            "rows": 0,
            "excel_path": output_path,
            "dataframe": df,
            "logs": logs,
        }

    total = len(lines)
    records: List[Dict] = []

    log(f"Starting Excel generation: mode={mode}, course='{course_name}', lines={total}.")

    for i, line in enumerate(lines, start=1):
        progress_callback(i, total)
        rec = _parse_line_to_record(line)
        records.append(rec)
        log(f"Parsed line {i}/{total}: {rec['Email'] or 'NO EMAIL'}")

    df = pd.DataFrame(records)

    # Extra columns useful for imports; adjust to your system needs
    df.insert(0, "Course", course_name)
    df.insert(1, "Role", mode.lower())

    try:
        df.to_excel(output_path, index=False)
        log(f"Excel saved to: {output_path}", "info")
    except Exception as e:
        log(f"Failed to save Excel to {output_path}: {e}", "error")

    return {
        "rows": len(df),
        "excel_path": output_path,
        "dataframe": df,
        "logs": logs,
    }

# core/excel_generation.py

"""Combine Excels Module"""

def _read_excel_generic(source: Union[str, IO[bytes]]) -> pd.DataFrame:
    """
    Read an Excel file from a file path or a file-like object.
    """
    return pd.read_excel(source)


def combine_excels(
    sources: List[Union[str, IO[bytes]]],
    output_path: str,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,
) -> Dict:
    """
    Combine multiple Excel sources (paths or file-like) into one DataFrame.
    """
    logs: List[Dict] = []

    def log(msg: str, level: str = "info"):
        entry = make_log_entry("ExcelCombine", msg, level)
        logs.append(entry)
        log_callback(entry)

    if not sources:
        log("No Excel sources provided to combine.", "warn")
        combined_df = pd.DataFrame()
        return {
            "rows": 0,
            "excel_path": output_path,
            "dataframe": combined_df,
            "logs": logs,
        }

    frames = []
    total = len(sources)

    for i, src in enumerate(sources, start=1):
        progress_callback(i, total)
        try:
            df = _read_excel_generic(src)
            df["__SourceIndex"] = i
            frames.append(df)
            log(f"Read Excel {i}/{total} – rows: {len(df)}", "info")
        except Exception as e:
            log(f"Failed to read Excel {i}/{total}: {e}", "error")

    if frames:
        combined_df = pd.concat(frames, ignore_index=True)
    else:
        combined_df = pd.DataFrame()

    try:
        combined_df.to_excel(output_path, index=False)
        log(f"Combined Excel saved to: {output_path}", "info")
    except Exception as e:
        log(f"Failed to save combined Excel to {output_path}: {e}", "error")

    return {
        "rows": len(combined_df),
        "excel_path": output_path,
        "dataframe": combined_df,
        "logs": logs,
    }




# core/search_users.py


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


# core/bulk_course_archive.py


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
