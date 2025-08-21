#!/usr/local/bin/python3

"""
## SETUP / Checklist

# Create virtual environment (replace `venv` with your preferred folder)
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Check Python Version
python3 -V

# Install Required Packages
pip install -r requirements.txt

⚠️ Avoid using:
#!/usr/bin/env python3

"""
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

3) Run
   python scrape_ce_users.py --input C:\Users\Neone\Downloads\VSCodes\PUBLIC_iLAMSAtmTool\c iLAMS_SearchUsers\4 docs_SearchUsers\04Apr25.csv \
   --url https://ilams.lamsinternational.com/lams/admin/usersearch.do

NOTES
-----
- Avoid '#!/usr/bin/env python3' per your requirement.
- Script will:
  * Read names from column A of input CSV (header optional).
  * Type name into the search input at: /html/body/div[1]/div/main/div[1]/div[2]/input
  * Scrape up to two result rows from the table.
  * Output CSV: YYYYMMDD_HHMMSS_dlcrosschecked.csv

"""

import os
import sys
import csv
import time
import random
import argparse
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)

import random
import time

if os.name == "nt":        # Windows
    os.system("cls")
else:                      # Linux / macOS
    os.system("clear")

"""
# 1) Path to your matching ChromeDriver
chrome_driver_path = r"C:\\Users\\Neone\\Driver\\chromedriver.exe"  
service = Service(chrome_driver_path)

# 2) Tell Selenium to hook into the existing Chrome debug port
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 3) Create the driver (this will *not* open a new browser window)
driver = webdriver.Chrome(service=service, options=options)

# 4) Confirm it s attached by printing the current title and URL
print("Attached to browser:", driver.title, driver.current_url)

"""

# === Setup ===
chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
# lams_course_mgmt_url = "https://ilams-bk.lamsinternational.com/lams/admin/orgmanage.do?org=1"
lams_search_users = "https://ilams.lamsinternational.com/lams/admin/usersearch.do"
csv_path = "lams_archived_courses.csv"

INPUT_FILE = "input_names.csv"   # your input file (column A = names)
OUTPUT_FILE = datetime.now().strftime("%Y%m%d_%H%M%S_dlcrosschecked.csv")


# -----------------------------
# CONSTANT XPATHS (from spec)
# -----------------------------
SEARCH_BAR_XPATH = "/html/body/div[1]/div/main/div[1]/div[2]/input"

TABLE_ROW1 = [
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[1]",  # User ID
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[2]",  # Login
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[3]",  # First Name
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[4]",  # Last Name
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[5]",  # Email
]

TABLE_ROW2 = [
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[1]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[2]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[3]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[4]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[5]",
]

# Fallback locators to wait on table presence (less brittle than absolute td XPaths)
TABLE_TBODY = "/html/body/div[1]/div/main/table/tbody"

# -----------------------------
# UTILS
# -----------------------------
def clear_console():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

def ts_filename(prefix: str, suffix: str) -> str:
    return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{prefix}.{suffix}"

def read_names_from_csv(path: Path) -> list[str]:
    names = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue
            name = (row[0] or "").strip()
            if not name:
                continue
            # If first row looks like a header (e.g., "Name"), keep it anyway—harmless—or skip:
            # if i == 0 and name.lower() in {"name", "names"}: continue
            names.append(name)
    return names

def build_driver(args) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # Attach to an existing Chrome debug session if requested/available
    if args.debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", args.debugger_address)

    # Headless optional (when NOT using debuggerAddress)
    if args.headless and not args.debugger_address:
        chrome_options.add_argument("--headless=new")

    # Chromedriver resolution:
    if args.chromedriver and Path(args.chromedriver).exists():
        service = Service(args.chromedriver)
    else:
        # fallback to PATH
        service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except WebDriverException as e:
        raise SystemExit(f"Failed to start Chrome WebDriver: {e}")

    return driver

def wait_for(driver, by, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def safe_text(driver, xpath: str) -> str:
    try:
        el = driver.find_element(By.XPATH, xpath)
        return el.text.strip()
    except NoSuchElementException:
        return ""
    except StaleElementReferenceException:
        # one quick retry
        time.sleep(0.25)
        try:
            el = driver.find_element(By.XPATH, xpath)
            return el.text.strip()
        except Exception:
            return ""

def jitter(base: float = 1.0, spread: float = 0.6) -> float:
    """Random sleep to reduce bot-like cadence."""
    return max(0.1, base + random.uniform(-spread, spread))

def try_search(driver, name: str, retries: int = 2) -> tuple[list[str], list[str]]:
    """
    Type into search box, submit, wait for results (tbody),
    then return tuple(row1_values, row2_values).
    If row not found, returns ["", "", "", "", ""] for that row.
    """
    last_err = None
    for attempt in range(retries + 1):
        try:
            # Ensure search bar is present
            box = wait_for(driver, By.XPATH, SEARCH_BAR_XPATH, timeout=10)
            box.clear()
            time.sleep(0.1)
            box.send_keys(name)
            box.send_keys(Keys.RETURN)

            # Wait for table body to (re)appear or update
            # If the page re-renders, presence_of_element is enough (we don't have an explicit spinner)
            wait_for(driver, By.XPATH, TABLE_TBODY, timeout=10)

            # tiny jitter to allow rows to render
            time.sleep(jitter(0.8, 0.4))

            row1 = [safe_text(driver, xp) for xp in TABLE_ROW1]
            row2 = [safe_text(driver, xp) for xp in TABLE_ROW2]

            # Heuristic: if all empty, maybe results truly empty or slow—one more micro-wait
            if not any(row1) and not any(row2):
                time.sleep(0.4)

            return row1, row2
        except (TimeoutException, StaleElementReferenceException) as e:
            last_err = e
            time.sleep(jitter(1.2, 0.6))
            continue
    # On failure, return empties
    return ["", "", "", "", ""], ["", "", "", "", ""]

# -----------------------------
# MAIN
# -----------------------------
def main():
    clear_console()

    parser = argparse.ArgumentParser(description="Scrape CE user table for up to two rows per name.")
    parser.add_argument("--input", required=True, help="Path to input CSV (names in column A).")
    parser.add_argument("--url", required=True, help="URL of the user search page.")
    parser.add_argument("--chromedriver", default="", help="Path to chromedriver binary (optional).")
    parser.add_argument("--debugger-address", default="127.0.0.1:9222",
                        help="Chrome DevTools debugger address (host:port). Leave as empty string to launch a fresh Chrome.")
    parser.add_argument("--headless", action="store_true", help="Run headless (ignored if using debugger address).")
    parser.add_argument("--sleep", type=float, default=1.2, help="Base sleep between searches (seconds).")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    # Output filename
    output_file = ts_filename("dlcrosschecked", "csv")
    output_path = Path.cwd() / output_file

    # Build driver and navigate
    driver = build_driver(args)
    try:
        driver.get(args.url)
        # Ensure the page is ready (search input present)
        wait_for(driver, By.XPATH, SEARCH_BAR_XPATH, timeout=20)
    except Exception as e:
        driver.quit()
        raise SystemExit(f"Failed to open search page or locate search input: {e}")

    # Read names
    names = read_names_from_csv(input_path)
    if not names:
        driver.quit()
        raise SystemExit("No names found in input CSV.")

    results_rows = []
    total = len(names)

    print(f"Found {total} names. Starting search...")

    for idx, name in enumerate(names, start=1):
        name_display = name.strip()
        if not name_display:
            continue

        print(f"[{idx}/{total}] Searching: {name_display}")

        row1, row2 = try_search(driver, name_display, retries=2)

        # If first row has any value -> record it; else mark NOT FOUND
        if any(cell for cell in row1):
            results_rows.append([name_display] + row1)
        else:
            # Explicit "NOT FOUND" in User ID field per your earlier convention
            results_rows.append([name_display, "NOT FOUND", "", "", "", ""])

        # If second row exists, record as "(Row2)"
        if any(cell for cell in row2):
            results_rows.append([f"{name_display} (Row2)"] + row2)

        # Polite pacing
        time.sleep(jitter(args.sleep, args.sleep * 0.4))

    # Write output
    headers = ["Name", "User ID", "Login", "First Name", "Last Name", "Email"]
    try:
        with output_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(results_rows)
    except Exception as e:
        driver.quit()
        raise SystemExit(f"Failed to write CSV: {e}")

    print(f"\n✅ Done! Exported results to {output_path}")
    try:
        print("Attached to browser:", driver.title, driver.current_url)
    except Exception:
        pass
    driver.quit()


if __name__ == "__main__":
    main()