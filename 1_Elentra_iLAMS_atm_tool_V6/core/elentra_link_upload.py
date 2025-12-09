# core/elentra_link_upload.py

from typing import Dict, List
import time

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


# STUDENT_URL_LOCATOR = (By.NAME, "student_url")  # example only
# MONITOR_URL_LOCATOR = (By.NAME, "monitor_url")  # example only
# SAVE_BUTTON_LOCATOR = (By.CSS_SELECTOR, "button[type='submit']")  # example only

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