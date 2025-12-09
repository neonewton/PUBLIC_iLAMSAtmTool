# core/selenium_utils.py

import os
from typing import Callable, Optional, List, Dict, Tuple
from datetime import datetime
import time
import subprocess
import socket

from .config import SeleniumConfig, get_config

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# Type aliases
LogCallback = Callable[[Dict], None]
ProgressCallback = Callable[[int, int], None]


def launch_chrome_with_debug(port=9222, retries=3, delay=1) -> bool:
    """
    Launch Google Chrome with remote debugging enabled.
    Supports macOS, Windows, Linux.
    """

    # --- DETECT OS ---
    is_windows = os.name == "nt"
    is_mac = os.name == "posix" and "darwin" in os.uname().sysname.lower()
    is_linux = os.name == "posix" and not is_mac

    # --- BUILD COMMAND PER OS ---
    if is_mac:
        # macOS: using "open -a"
        profile_dir = os.path.expanduser("~/chrome-debug-profile")
        launch_cmd = [
            "open", "-a", "Google Chrome",
            "--args",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
        ]

    else:
        # Windows command
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        profile_dir = os.path.expanduser(r"~\chrome-debug-profile")

        launch_cmd = [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
        ]

    print(f"Using Chrome launch command: {launch_cmd}")

    # --- RETRY LOOP ---
    for attempt in range(1, retries + 1):
        print(f"Launching Chrome (attempt {attempt}/{retries})...")

        try:
            subprocess.Popen(launch_cmd)
            time.sleep(2)  # let Chrome start

            # Test if port is open
            s = socket.socket()
            try:
                s.settimeout(1)
                s.connect(("127.0.0.1", port))
                s.close()
                print(f"Chrome debugging port {port} is open.")
                return True
            except Exception:
                print(f"Port {port} not open yet (attempt {attempt}).")

        except Exception as e:
            print(f"Failed to launch Chrome: {e}")

        time.sleep(delay)

    print(f"❌ Chrome failed to start after {retries} attempts.")
    return False


def default_log_callback(entry: Dict) -> None:
    """Fallback logger that prints to stdout."""
    print(f"[{entry.get('timestamp')}] [{entry.get('level', 'INFO')}] "
          f"{entry.get('feature', '')}: {entry.get('message', '')}")


def default_progress_callback(current: int, total: int) -> None:
    """Fallback progress callback that does nothing."""
    pass


def make_log_entry(feature: str, message: str, level: str = "info") -> Dict:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "feature": feature,
        "level": level.upper(),
        "message": message,
    }


def get_driver(
    config: Optional[SeleniumConfig] = None,
):
    """
    Create a Selenium Chrome driver attached to an existing Chrome session
    via remote debugging.
    """
    if config is None:
        config = get_config()

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", config.debugger_address)

    service = Service(config.driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    return driver, wait

time_sleep = 0.5 #1 sec or 0.5 sec # wait x seconds between actions, for presentation purposes
time_out = 10 #wait up to x seconds for element to be clickable
highlight_duration = 1 #set in def highlight ()

def wait_and_click(
    driver,
    locator,
    description: str = None,
    timeout=10,
    log_callback=default_log_callback,
    highlight_fn=None,
    sleep_after=None,
    message=None,   # <-- allow backward compatibility
):

    # Backward compatibility: if caller uses message=
    if message and not description:
        description = message
    if not description:
        description = "element"

    # Allow simple XPath string
    if isinstance(locator, str):
        locator = (By.XPATH, locator)

    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable(locator))

    # Highlight if function provided
    if highlight_fn:
        highlight_fn(driver, element)

    element.click()

    log_callback(make_log_entry("SeleniumUtils", f"Clicked: {description}"))

    if sleep_after:
        time.sleep(sleep_after)



def click_text(
    driver,
    text,
    timeout=10,
    log_callback=default_log_callback,
    highlight_fn=None,
    sleep_after=None,
):
    locator = (By.XPATH, f"//*[contains(text(), '{text}')]")
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable(locator))

    if highlight_fn:
        highlight_fn(element)

    element.click()
    log_callback(make_log_entry("SeleniumUtils", f"Clicked text: {text}"))

    if sleep_after:
        time.sleep(sleep_after)



def dramatic_input(wait, locator, text: str, description: str,
                  clear: bool = True,
                  log_callback: LogCallback = default_log_callback):
    """Wait for an element, then type text into it."""
    from selenium.webdriver.support import expected_conditions as EC

    element = wait.until(EC.visibility_of_element_located(locator))
    if clear:
        element.clear()
    element.send_keys(text)
    log_callback(make_log_entry("SeleniumUtils", f"Typed into {description}: {text}"))


def highlight(el, duration=highlight_duration, color="clear", border="3px solid red"):
    """Highlight an element reliably by injecting CSS with !important."""
    try:
        driver = el._parent  

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", el)

        # Save original style
        original_style = el.get_attribute("style") or ""

        # Apply strong highlight with !important
        highlight_style = (
            f"background: {color} !important;"
            f"border: {border} !important;"
            f"outline: {border} !important;"
            f"box-shadow: {border} !important;"
            f"{original_style}"
        )

        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            el,
            highlight_style,
        )

        time.sleep(duration)

        # Restore previous style
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            el,
            original_style,
        )

    except Exception as e:
        print(f"Highlight failed: {e}")


def check_selenium_environment(
    config: Optional[SeleniumConfig] = None,
) -> Tuple[bool, List[Dict]]:
    """
    Perform a series of sanity checks:
    - chromedriver path exists
    - selenium package importable
    - can start driver attached to debuggerAddress
    - optional: can open base URL(s)
    """
    if config is None:
        config = get_config()

    logs: List[Dict] = []
    feature = "PreChecks"

    def log(msg: str, level: str = "info"):
        entry = make_log_entry(feature, msg, level)
        logs.append(entry)

    ok = True

    # Check chromedriver path
    if not os.path.exists(config.driver_path):
        log(f"Chromedriver not found at path: {config.driver_path}", "error")
        ok = False
    else:
        log(f"Chromedriver path OK: {config.driver_path}", "info")

    # Check selenium import
    try:
        import selenium  # noqa: F401
        log("Selenium package import OK.", "info")
    except Exception as e:
        log(f"Failed to import selenium: {e}", "error")
        ok = False

    if not ok:
        return False, logs

    # Try to attach to Chrome via debuggerAddress
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.support.ui import WebDriverWait

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", config.debugger_address)
        service = Service(config.driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)

        log(f"Attached to Chrome at {config.debugger_address}", "info")

        # Optionally hit LAMS base URL
        if config.lams_base_url:
            driver.get(config.lams_base_url)
            log(f"Opened LAMS base URL: {config.lams_base_url}", "info")

        # Optionally hit Elentra base URL
        if config.elentra_base_url:
            driver.get(config.elentra_base_url)
            log(f"Opened Elentra base URL: {config.elentra_base_url}", "info")

        driver.quit()
        log("Driver started and closed successfully.", "info")

    except Exception as e:
        log(f"Failed to start driver or navigate: {e}", "error")
        ok = False

    return ok, logs
