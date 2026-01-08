# core/elentra_link_upload.py


import re
from typing import Dict, List, Any, Union, IO, Callable
import time
from datetime import datetime

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

def _parse_multi_input(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,\n]+", text)
    return [p.strip() for p in parts if p.strip()]

def run_elentra_link_upload(
    lams_lesson_titles_raw: str,
    elentra_event_ids_raw: str,
    lams_lesson_ids_raw: str,
    upload_student: bool,
    upload_monitor: bool,
    log_callback: LogCallback = default_log_callback,
    progress_callback: ProgressCallback = default_progress_callback,

) -> List[Dict]:
    start_time = time.time() 

    lams_lesson_titles = _parse_multi_input(lams_lesson_titles_raw)
    lams_lesson_ids = _parse_multi_input(lams_lesson_ids_raw)
    elentra_event_ids = _parse_multi_input(elentra_event_ids_raw)

    # Input validation
    if not (lams_lesson_titles and lams_lesson_ids and elentra_event_ids):
        raise ValueError(
            "Lesson Title, LAMS Lesson ID, and Elentra Event ID cannot be empty."
        )

    if not (
        len(lams_lesson_titles)
        == len(lams_lesson_ids)
        == len(elentra_event_ids)
    ):
        raise ValueError(
            "Number of Lesson Titles, LAMS Lesson IDs, and Elentra Event IDs must be the same."
        )

    for i, title in enumerate(lams_lesson_titles, start=1):
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Lesson Title at row {i} is invalid.")

    lesson_ids = []
    for i, lid in enumerate(lams_lesson_ids, start=1):
        if not lid.isdigit():
            raise ValueError(f"LAMS Lesson ID at row {i} must be an integer.")
        lesson_ids.append(int(lid))

    event_ids = []
    for i, eid in enumerate(elentra_event_ids, start=1):
        if not eid.isdigit():
            raise ValueError(f"Elentra Event ID at row {i} must be an integer.")
        event_ids.append(int(eid))

    logs: List[Dict] = []

    def log(msg: str, level: str = "INFO"):
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "module": "ElentraUpload",
            "level": level,
            "message": msg,
        }
        logs.append(entry)
        log_callback(entry)


    config = get_config()

    def should_stop():
        return st.session_state.get("stop_requested", False)

    if not config.elentra_base_url:
        log("Elentra base URL is not configured. Set it in Home page.", "error")
        return logs

    try:
        
        driver, wait = get_driver(config)
        total = len(lams_lesson_titles)
        results = []

    
        for idx in range(total):


            if should_stop():
                log("🛑 Stop requested — stopping.")
                return logs

            lams_lesson_title = lams_lesson_titles[idx]
            lams_lesson_id = lams_lesson_ids[idx]
            elentra_event_id = event_ids[idx]

            log(f"[{idx+1}/{total}] Processing {lams_lesson_title}")

            elentra_event_url = (
                f"https://ntu.elentra.cloud/events?id={elentra_event_id}"
            )

            lams_monitor_title = f"LAMS {lams_lesson_title} (Facilitator/CE)"
            lams_monitor_url = (
                "https://ilams.lamsinternational.com/lams/monitoring/"
                f"monitoring/monitorLesson.do?lessonID={lams_lesson_id}"
            )

            lams_student_title = f"LAMS {lams_lesson_title}"
            lams_student_url = (
                "https://ilams.lamsinternational.com/lams/home/learner.do?"
                f"lessonID={lams_lesson_id}"
            )

            log(f"[{idx+1}/{total}] Processing {lams_lesson_title}")
            
            try:


                # STEP 1: Attach to Selenium
                log("Attached to Selenium driver.")

                # STEP 2: Open Elentra Event Page (Twice)
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
                if should_stop():
                    log("🛑 Stop requested — stopping.")
                    return logs

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
                    log("⏳ Inserting MONITOR URL...")

                    if should_stop():
                        log("🛑 Stop requested — stopping.")
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

                    if should_stop():
                        log("🛑 Stop requested — stopping.")
                        return logs
                    
                    # Save + Close
                    wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", timeout=time_out,
                                highlight_fn=highlight, message="Monitor resource saved", sleep_after=time_sleep)
                    wait_and_click(driver, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]", timeout=time_out,
                                highlight_fn=highlight, message="Monitor resource dialog closed", sleep_after=time_sleep)

                # ----------------------------------------------
                # STEP 6: STUDENT RESOURCE WORKFLOW
                # ----------------------------------------------
                if upload_student:

                    log("⏳ Inserting STUDENT URL...")

                    if should_stop():
                        log("🛑 Stop requested — stopping.")
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

                    if should_stop():
                        log("🛑 Stop requested — stopping.")
                        return logs

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

                    if should_stop():
                        log("🛑 Stop requested — stopping.")
                        return logs

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

                    results.append({
                        "lesson_title": lams_lesson_title,
                        "lams_lesson_id": lams_lesson_id,
                        "elentra_event_id": elentra_event_id,
                        "status": "success",
                    })
                    progress_callback(idx + 1, total)
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
                log(f"❌ Failed lesson {idx+1}: {e}", "error")
                results.append({
                    "lesson_title": lams_lesson_title,
                    "lams_lesson_id": lams_lesson_id,
                    "elentra_event_id": elentra_event_id,
                    "status": f"error: {e}",
                })
                continue

            progress_callback(idx + 1, total)

    finally:
        if driver is not None:
            try:
                driver.quit()
                log("🧹 Selenium driver closed")
            except Exception:
                pass

    elapsed = time.time() - start_time
    log(f"⏱ Total elapsed time: {elapsed:.1f} seconds")

    return {
        "logs": logs,
        "results": results,
    }


