#!/usr/local/bin/python3
# shift cmd P to select 3.13 
# DO NOT USE !/usr/bin/env python3

# Ensure you have started Chrome with:
r"""
MAC:
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"
then
curl http://127.0.0.1:9222/json

WINDOWS:
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  --remote-debugging-port=9222 `
  --user-data-dir="C:\Users\Neone\chrome-debug-profile"
then
curl http://127.0.0.1:9222/json
"""

import sys
import os
import time
import platform
import logging
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException

# ==== CONFIGURATION CONSTANTS ====
CHROME_DRIVER_PATHS = {
    "Darwin": "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver",
    "Windows": r"C:\WebDrivers\chromedriver-win64\chromedriver.exe"
}

DEBUGGER_ADDRESS = "127.0.0.1:9222"
WAIT_TIME_AFTER_ACTION = 1.5 #1 sec or 0.05 sec # wait x seconds between actions, for presentation purposes
ELEMENT_TIMEOUT = 10 #wait up to x seconds for element to be clickable
HIGHLIGHT_DURATION = 0.1 #highlight_duration = 0.05 set in def highlight ()
# ================================

# ==== LOGGER SETUP ====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global driver reference
driver = None

# ==== DRIVER SETUP ====
def setup_driver():
    """Initialize and return a Chrome WebDriver attached to an existing debug session."""
    system = platform.system()
    driver_path = CHROME_DRIVER_PATHS.get(system)
    if not driver_path:
        raise RuntimeError(f"Unsupported OS for driver: {system}")
    service = Service(executable_path=driver_path)
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)
    drv = webdriver.Chrome(service=service, options=options)
    drv.maximize_window()
    ui_log("✅ Chrome WebDriver attached to existing session")
    return drv

# ==== UI LOGGING ====
ui_root = None
log_widget = None

def ui_log(message: str):
    """Log to both ScrolledText widget and standard logger."""
    logger.info(message)
    if log_widget:
        log_widget.config(state="normal")
        log_widget.insert("end", message + "\n")
        log_widget.see("end")
        log_widget.config(state="disabled")
        ui_root.update_idletasks()

# ==== HIGHLIGHT HELPER ====
def highlight(el, duration=HIGHLIGHT_DURATION, color="transparent", border="4px solid red"):
    """Briefly highlight an element for visibility."""
    try:
        drv = el.parent
        original = el.get_attribute("style") or ""
        hl_style = f"background: {color} !important; border: {border} !important; {original}"
        drv.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].setAttribute('style', arguments[1]);",
            el, hl_style
        )
        time.sleep(duration)
        drv.execute_script("arguments[0].setAttribute('style', arguments[1]);", el, original)
    except Exception:
        pass

# ==== UNIFIED INTERACTION ====
def wait_and_interact(driver, locator, action="click", value=None, description=None):
    """
    Wait for element by absolute XPath, highlight, perform action, log, and pause.
    locator: tuple(By.XPATH, xpath)
    action: "click" | "send_keys" | "get_text"
    """
    try:
        if action == "click":
            el = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
                EC.element_to_be_clickable(locator)
            )
        elif action == "send_keys":
            el = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
                EC.visibility_of_element_located(locator)
            )
        elif action == "get_text":
            el = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(locator)
            )
        else:
            raise ValueError(f"Unknown action: {action}")

        highlight(el)
        if action == "click":
            el.click()
        elif action == "send_keys":
            el.clear()
            el.send_keys(value)
        elif action == "get_text":
            text = el.text

        if description:
            ui_log(f"✅ {description}")
        time.sleep(WAIT_TIME_AFTER_ACTION)
        if action == "get_text":
            return text

    except (TimeoutException, WebDriverException) as e:
        messagebox.showerror("Interaction Error", f"Failed {action} on {locator[1]}: {e}")
        logger.error("Failed %s on %s: %s", action, locator[1], e)
        raise

# ==== RESOURCE FLOW ====
def add_resource_flow(driver, resource_url, resource_title, is_monitor_url: bool):
    """
    Execute the absolute-XPath sequence to add a Monitor or Student resource.
    """
    prefix = "MONITOR" if is_monitor_url else "STUDENT"
    ui_log(f"⏳ Inserting {prefix} URL ⏳")

    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    ui_log("✅ Scrolled to bottom")

    # Step sequence using absolute XPaths
    steps = [
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/ul/li[4]/a", "No Time Frame link clicked"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/div[1]/a", "Add a Resource link clicked"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div/label[6]", "Link checkbox selected"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", "Next Step clicked"),
    ]
    for xpath, msg in steps:
        wait_and_interact(driver, (By.XPATH, xpath), "click", description=msg)

    # Optional/Required
    opt_xpath = "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]" if is_monitor_url else "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[2]"
    wait_and_interact(driver, (By.XPATH, opt_xpath), "click", description=("Optional" if is_monitor_url else "Required") + " selected")

    # Continue fixed sequence
    fixed = [
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/label[4]", "No Timeframe selected"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", "Next step to Hide clicked"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[2]" if is_monitor_url else "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[1]", ("Hide this resource from learners" if is_monitor_url else "Allow learners to view this resource") + " selected"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[4]/label[1]", "Published selected"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]", "Final Next Step clicked"),
        ("/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/div/label[1]", "Proxy not required selected"),
    ]
    for xpath, msg in fixed:
        wait_and_interact(driver, (By.XPATH, xpath), "click", description=msg)

    # Insert URL and Title
    wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/div/input"), "send_keys", value=resource_url, description="URL entered")
    wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/div/input"), "send_keys", value=resource_title, description="Title entered")

    # Scroll modal
    modal = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, "event-resource-modal"))
    )
    highlight(modal)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", modal)
    ui_log("✅ Modal scrolled to bottom")
    time.sleep(WAIT_TIME_AFTER_ACTION)

    # Description iframe
    iframe = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[5]/iframe"))
    )
    driver.switch_to.frame(iframe)
    editor = WebDriverWait(driver, ELEMENT_TIMEOUT).until(
        EC.presence_of_element_located((By.XPATH, "/html/body"))
    )
    highlight(editor)
    editor.send_keys(Keys.COMMAND + "a", Keys.DELETE)
    editor.send_keys(resource_title)
    driver.switch_to.default_content()
    ui_log("✅ Description added")
    time.sleep(WAIT_TIME_AFTER_ACTION)

    # Save & Close
    wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"), "click", description="Resource saved")
    wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]"), "click", description="Closed attachment dialog")

# ==== MAIN AUTOMATION ====
def run_automation(event_id, lesson_id, lesson_title, use_monitor, use_student):
    global driver
    start = time.time()
    for w in (eid_entry, lid_entry, title_entry, mon_chk, stu_chk, ok_btn, close_btn):
        w.config(state="disabled")

    try:
        # Build URLs & titles
        elentra_url = f"https://ntu.elentra.cloud/events?id={event_id}"
        mon_url = f"https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID={lesson_id}"
        mon_title = f"LAMS {lesson_title} (Facilitator/CE)"
        stu_url = f"https://ilams.lamsinternational.com/lams/home/learner.do?lessonID={lesson_id}"
        stu_title = f"LAMS {lesson_title}"
        ui_log("✅ URLs and titles constructed")

        driver = setup_driver()
        if not driver: return
        driver.get(elentra_url)
        ui_log("✅ Navigated to Elentra event page")
        time.sleep(WAIT_TIME_AFTER_ACTION)

        # Administrator checkbox
        wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[3]/div[2]/ul/li[2]/a/span"), "click", description="Administrator" )
        # Content tab
        wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/div[2]/ul/li[2]/a"), "click", description="Content tab")
        # Page title
        title = wait_and_interact(driver, (By.XPATH, "/html/body/div[1]/div/div[3]/div/h1[1]"), "get_text", description="Page title extracted")
        ui_log(f"✅ Page title: {title}")

        # Add resources
        if use_monitor:
            add_resource_flow(driver, mon_url, mon_title, True)
        if use_student:
            add_resource_flow(driver, stu_url, stu_title, False)

        ui_log(f"🎉 Completed in {time.time()-start:.1f}s")
    except Exception as e:
        ui_log(f"❌ Automation failed: {e}")
        messagebox.showerror("Automation Error", str(e))
    finally:
        ui_log(f"⏱ Total elapsed time: {time.time()-start:.1f}s")
        for w in (eid_entry, lid_entry, title_entry, mon_chk, stu_chk, ok_btn, close_btn):
            w.config(state="normal")
        # driver.quit()

# ==== TKINTER UI ====
def get_user_choices(
    event_default="1696",
    lesson_default="37655",
    lesson_title_default="(RPA test)FM_MiniQuiz_WomanHealth_DDMMYY"
):
    global ui_root, log_widget, eid_entry, lid_entry, title_entry, mon_chk, stu_chk, ok_btn, close_btn

    ui_root = tk.Tk()
    ui_root.title("LAMS RPA Tool")
    ui_root.resizable(True, True)
    ui_root.minsize(800, 600)
    ui_root.grid_columnconfigure(0, weight=0)
    ui_root.grid_columnconfigure(1, weight=1)

    # Input vars
    eid_var = tk.StringVar(value=event_default)
    lid_var = tk.StringVar(value=lesson_default)
    title_var = tk.StringVar(value=lesson_title_default)
    mon_var = tk.BooleanVar(value=True)
    stu_var = tk.BooleanVar(value=True)

    pad = dict(padx=8, pady=6)
    tk.Label(ui_root, text="Elentra Event ID:").grid(row=0, column=0, sticky="w", **pad)
    eid_entry = tk.Entry(ui_root, textvariable=eid_var);
    eid_entry.grid(row=0, column=1, sticky="ew", **pad)
    tk.Label(ui_root, text="LAMS Lesson ID:").grid(row=1, column=0, sticky="w", **pad)
    lid_entry = tk.Entry(ui_root, textvariable=lid_var)
    lid_entry.grid(row=1, column=1, sticky="ew", **pad)
    tk.Label(ui_root, text="LAMS Lesson Title:").grid(row=2, column=0, sticky="w", **pad)
    title_entry = tk.Entry(ui_root, textvariable=title_var)
    title_entry.grid(row=2, column=1, sticky="ew", **pad)

    mon_chk = tk.Checkbutton(ui_root, text="Upload Monitor URL", variable=mon_var)
    mon_chk.grid(row=3, columnspan=2, sticky="w", **pad)
    stu_chk = tk.Checkbutton(ui_root, text="Upload Student URL", variable=stu_var)
    stu_chk.grid(row=4, columnspan=2, sticky="w", **pad)

    log_widget = ScrolledText(ui_root, wrap="word", height=10, state="disabled")
    log_widget.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=8, pady=(0,4))
    ui_root.grid_rowconfigure(5, weight=1)

    # Handlers
    def on_ok():
        if not (mon_var.get() or stu_var.get()):
            messagebox.showerror("Selection error", "Select at least one URL to upload.")
            return
        if not eid_var.get().strip() or not lid_var.get().strip() or not title_var.get().strip():
            messagebox.showerror("Input error", "Ensure all fields are filled.")
            return
        ui_log("🏁 Starting automation...")
        ui_root.after(100, lambda: run_automation(
            eid_var.get().strip(), lid_var.get().strip(), title_var.get().strip(), mon_var.get(), stu_var.get()
        ))

    def on_cancel():
        if driver:
            try:
                driver.quit()
            except:
                pass
        ui_root.destroy()
        sys.exit(0)

    # Buttons
    btn_frame = tk.Frame(ui_root)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=8)
    ok_btn = tk.Button(btn_frame, text="Start Automation", command=on_ok, width=20)
    ok_btn.pack(side="left", padx=5)
    close_btn = tk.Button(btn_frame, text="Close", command=on_cancel, width=20)
    close_btn.pack(side="left", padx=5)

    ui_root.protocol("WM_DELETE_WINDOW", on_cancel)
    ui_root.mainloop()

# ==== ENTRY POINT ====
if __name__ == "__main__":
    print("Using Python executable:", sys.executable)
    get_user_choices()

