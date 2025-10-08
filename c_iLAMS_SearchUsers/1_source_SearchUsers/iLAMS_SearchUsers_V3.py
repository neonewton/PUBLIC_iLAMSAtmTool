#!/usr/local/bin/python3

"""
## SETUP / Checklist

# Create virtual environment (replace `venv` with your preferred folder)
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

Windows
venv\Scripts\activate

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
#!/usr/local/bin/python3
"""
Setup notes omitted for brevity. Scroll down for logic.
"""

import os
import csv
import time
import random
import re
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
CSV_INPUT_PATH = r"C:\Users\Neone\Downloads\VSCodes\PUBLIC_iLAMSAtmTool\c_iLAMS_SearchUsers\4_docs_SearchUsers\11Nov25.csv"
CHROMEDRIVER_PATH = r"C:\Users\Neone\Driver\chromedriver.exe"
LAMS_URL = "https://ilams.lamsinternational.com/lams/admin/usersearch.do"
TIMESLEEP = 1.5

# === PATH SETUP ===
input_path = Path(CSV_INPUT_PATH)
input_dir = input_path.parent
input_filename = input_path.stem  # e.g. "10Oct25v2_test"
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

OUTPUT_PATH_RAW = input_dir / f"{input_filename}_ilams_{timestamp}.csv"
OUTPUT_PATH_ENRICHED = input_dir / f"{input_filename}_dlcrosschecked_{timestamp}.csv"

# === ELEMENT XPATHS ===
SEARCH_INPUT = "/html/body/div[1]/div/main/div[1]/div[2]/input"
TABLE_ROW1 = [f"/html/body/div[1]/div/main/table/tbody/tr[1]/td[{i}]" for i in range(1, 6)]
TABLE_ROW2 = [f"/html/body/div[1]/div/main/table/tbody/tr[2]/td[{i}]" for i in range(1, 6)]

# === HELPERS ===
def safe_text(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except (NoSuchElementException, StaleElementReferenceException):
        return ""

# === INIT BROWSER ===
if os.name == "nt": os.system("cls")
else: os.system("clear")

options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

print("✅ Attached to Chrome")
driver.get(LAMS_URL)
wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT)))

# === LOAD INPUT ===
input_rows = []
name_pairs = []

with open(CSV_INPUT_PATH, newline='', encoding="windows-1252") as f:
    reader = csv.reader(f)
    headers = next(reader)  # header row
    for row in reader:
        if row and row[0].strip():
            original_name = row[0].strip()
            cleaned_name = re.sub(r"\s*\(.*?\)", "", original_name)
            input_rows.append(row)
            name_pairs.append((original_name, cleaned_name))

# === MAIN LOOP ===
results = []
combined_output = []

for idx, ((original_name, cleaned_name), original_row) in enumerate(zip(name_pairs, input_rows), start=1):
    print(f"[{idx}/{len(name_pairs)}] Searching: {cleaned_name}")
    
    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, SEARCH_INPUT)))
        search_box.clear()
        time.sleep(0.2)
        search_box.send_keys(cleaned_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(TIMESLEEP)

        row1 = [safe_text(driver, xp) for xp in TABLE_ROW1]
        row2 = [safe_text(driver, xp) for xp in TABLE_ROW2]

        # Output 1: Raw scrape
        if any(row1):
            results.append([original_name] + row1)
        else:
            results.append([original_name, "NOT FOUND", "", "", "", ""])

        if any(row2):
            results.append([f"{original_name} (Row2)"] + row2)

        # Output 2: Enriched
        if any(row1) and any(row2):
            status = "Acc >1"
        elif any(row1):
            status = "Exist"
        else:
            status = "Acc Not Found"

        ilams_email_1 = row1[4] if len(row1) > 4 else ""
        ilams_email_2 = row2[4] if len(row2) > 4 else ""

        enriched_row = original_row + [status, ilams_email_1]
        combined_output.append(enriched_row)

        if status == "Acc >1":
            alt_row = original_row.copy()
            alt_row[0] = f"{original_name} (Row2)"
            alt_row += [status, ilams_email_2]
            combined_output.append(alt_row)

    except Exception as e:
        print(f"❌ Error processing {cleaned_name}: {e}")
        results.append([original_name, "ERROR", "", "", "", ""])
        error_row = original_row + ["ERROR", ""]
        combined_output.append(error_row)
        continue

    time.sleep(random.uniform(0.8, 1.6))

# === SAVE OUTPUT ===
with open(OUTPUT_PATH_RAW, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["Name", "User ID", "Login", "First Name", "Last Name", "Email"])
    writer.writerows(results)

with open(OUTPUT_PATH_ENRICHED, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(headers + ["DL check account?", "iLAMS email address"])
    writer.writerows(combined_output)

print(f"\n✅ Finished.")
print(f"📁 Raw scrape saved to: {OUTPUT_PATH_RAW.name}")
print(f"📁 Enriched merge saved to: {OUTPUT_PATH_ENRICHED.name}")

driver.quit()
