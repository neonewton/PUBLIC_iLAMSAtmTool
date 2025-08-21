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
import csv
import time
import random
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
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)

# === USER CONFIG ===
CSV_INPUT_PATH = r"C:\Users\Neone\Downloads\VSCodes\PUBLIC_iLAMSAtmTool\c_iLAMS_SearchUsers\4_docs_SearchUsers\10Oct25.csv"
CHROMEDRIVER_PATH = r"C:\Users\Neone\Driver\chromedriver.exe"

LAMS_URL = "https://ilams.lamsinternational.com/lams/admin/usersearch.do"
TIMESLEEP = 1.5

input_path = Path(CSV_INPUT_PATH)
input_filename = input_path.name  
input_dir = input_path.parent     # Folder of the input file

# Output to same folder with timestamp
OUTPUT_PATH = input_dir / f"{input_filename}_{datetime.now().strftime('20%y%m%d_%H%M%S')}.csv"

# XPaths
SEARCH_INPUT = "/html/body/div[1]/div/main/div[1]/div[2]/input"
TABLE_ROW1 = [
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[1]",
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[2]",
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[3]",
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[4]",
    "/html/body/div[1]/div/main/table/tbody/tr[1]/td[5]",
]
TABLE_ROW2 = [
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[1]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[2]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[3]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[4]",
    "/html/body/div[1]/div/main/table/tbody/tr[2]/td[5]",
]

def safe_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except (NoSuchElementException, StaleElementReferenceException):
        return ""

# === Initialise ===
if os.name == "nt":
    os.system("cls")
else:
    os.system("clear")

# Attach to existing Chrome session
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

print("✅ Attached to Chrome")

# Go to the page
driver.get(LAMS_URL)
wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT)))

# Load names
with open(CSV_INPUT_PATH, newline='', encoding="windows-1252") as f:
    reader = csv.reader(f)
    import re  # <-- Make sure this is at the top of your script
    names = [
        re.sub(r"\s*\(.*?\)", "", row[0].strip())  # removes (TTSH), (abc), etc.
        for row in reader
        if row and row[0].strip()
    ]

results = []

# Search each name
for idx, name in enumerate(names, start=1):
    print(f"[{idx}/{len(names)}] Searching: {name}")

    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT)))
        search_box.clear()
        time.sleep(0.2)
        search_box.send_keys(name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(TIMESLEEP)

        row1 = [safe_text(driver, xp) for xp in TABLE_ROW1]
        row2 = [safe_text(driver, xp) for xp in TABLE_ROW2]

        if any(row1):
            results.append([name] + row1)
        else:
            results.append([name, "NOT FOUND", "", "", "", ""])

        if any(row2):
            results.append([f"{name} (Row2)"] + row2)

    except Exception as e:
        print(f"❌ Error processing {name}: {e}")
        results.append([name, "ERROR", "", "", "", ""])
        continue

    time.sleep(random.uniform(0.8, 1.6))

# Write results
with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "User ID", "Login", "First Name", "Last Name", "Email"])
    writer.writerows(results)

print(f"\n✅ Finished. CSV saved to:\n{OUTPUT_PATH}")
driver.quit()
