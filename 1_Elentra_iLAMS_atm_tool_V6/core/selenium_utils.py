# core/selenium_utils.py

import os
from typing import Callable, Optional, List, Dict, Tuple
from datetime import datetime

from .config import SeleniumConfig, get_config

# Type aliases
LogCallback = Callable[[Dict], None]
ProgressCallback = Callable[[int, int], None]


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

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", config.debugger_address)

    service = Service(config.driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)

    return driver, wait


def wait_and_click(wait, locator, description: str, log_callback: LogCallback = default_log_callback):
    """Wait for an element to be clickable, then click it."""
    from selenium.webdriver.support import expected_conditions as EC

    element = wait.until(EC.element_to_be_clickable(locator))
    element.click()
    log_callback(make_log_entry("SeleniumUtils", f"Clicked: {description}"))


def wait_and_type(wait, locator, text: str, description: str,
                  clear: bool = True,
                  log_callback: LogCallback = default_log_callback):
    """Wait for an element, then type text into it."""
    from selenium.webdriver.support import expected_conditions as EC

    element = wait.until(EC.visibility_of_element_located(locator))
    if clear:
        element.clear()
    element.send_keys(text)
    log_callback(make_log_entry("SeleniumUtils", f"Typed into {description}: {text}"))


def highlight_element(driver, element):
    """Optional: highlight element during automation for visual debugging."""
    driver.execute_script(
        "arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='#ffffcc';",
        element,
    )


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
