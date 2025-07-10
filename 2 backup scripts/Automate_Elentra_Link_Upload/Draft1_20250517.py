"""
Automation Steps:

1. Configuration
   • Hard-code or load Elentra Event ID and LAMS Lesson ID
   • Build:
       - elentra_url = "https://ntu.elentra.cloud/events?id=<EVENT_ID>"
       - monitor_url = "https://ilams.lamsinternational.com/...monitorLesson.do?lessonID=<LESSON_ID>"
       - monitor_title = "Monitor for Lesson <LESSON_ID>"

2. Browser Setup
   • Manually launch Chrome with:
       open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-debug-profile"
   • In code, attach Selenium to that session via debuggerAddress=127.0.0.1:9222

3. Navigate to Event Page
   • driver.get(elentra_url)
   • wait 2 s

4. Dashboard Link
   • wait until dashboard link XPath is clickable → click it

5. Select Resource
   • wait until resource-checkbox XPath is clickable → click it

6. Open Content Tab
   • click “Content” tab XPath
   • pause 1 s

7. Scroll & Settings
   • scroll to bottom of page
   • click “No Time Frame” XPath
   • pause 1 s

8. Add Resource Wizard
   a. Click “Add a Resource”
   b. Select “Link” checkbox
   c. Wizard Page Flow:
      1) Click “Next Step” → select “Optional”
      2) Click “Next Step” → select “Hide this resource from learners”
      3) Click “Next Step” to reach URL form

9. Fill In Link Details
   • Clear pre-filled URL field → dramatic_input(monitor_url)
   • Clear title field → dramatic_input(monitor_title)
   • Clear/generate description textarea → dramatic_input("Auto-added link for lesson <ID>")
   • pause 1 s between each

10. Save & Teardown
    • Click “Save Resource”
    • pause 1 s
    • Print success or catch/print exception
    • driver.quit()
"""

#!/usr/bin/env python3
import sys
import os
os.system('clear')
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Ensure you have started Chrome with:
"""
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"

then

curl http://127.0.0.1:9222/json
"""

# Check which Python interpreter is in use
print("Using Python executable:", sys.executable)

def dramatic_input(element, text, delay=0.01):
    """Type each character with a small pause to mimic a human."""
    for ch in text:
        element.send_keys(ch)
        time.sleep(delay)

def main():
    time_sleep = 2

    # 1) Prompt for IDs
    """
    elentra_event_id = input("Enter Elentra event ID: ").strip()
    lams_lesson_id   = input("Enter LAMS lesson ID: ").strip()
    monitor_title = input("Enter Monitor title: ").strip()
    """
    elentra_event_id = "1696"
    lams_lesson_id = "37655"
    monitor_title = "(test)FM_MiniQuiz_WomanHealth_DDMMYY"
    
    """
    """
    print("✅ ID input")

    # 2) Build URLs & Title
    elentra_url   = f"https://ntu.elentra.cloud/events?id={elentra_event_id}"
    monitor_url   = f"https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID={lams_lesson_id}"
    
    print("✅ URL input")

    # 3) Setup Chrome WebDriver to attach to existing debug session
    chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
    service = Service(executable_path=chrome_driver_path)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome WebDriver started")

    try:
        
    
        # 4) Navigate to Elentra Event Page
        driver.get(elentra_url)
        print("✅ Navigated to Elentra event page")
        time.sleep(time_sleep)

        # # SSO Login
        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH,
        #         "/html/body/div/div/div/div/div[2]/div[1]/div[1]/div/div/a"
        #     ))
        # ).click()
        # print("✅ SSO Login")
        
        # # 4.5) Wait for the Adminstrator checkbox link to be clickable, then click
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "/html/body/div[1]/div/div[2]/div[2]/div[3]/div[2]/ul/li[2]/a/span"
            ))
        ).click()
        print("✅ Adminstrator checkbox clicked")

        # 6) Click “Content”
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "/html/body/div[1]/div/div[3]/div/div[2]/ul/li[2]/a"
            ))
        ).click()
        print("✅ Content link clicked")
        time.sleep(time_sleep)

        # 7) Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("✅ Scrolled to bottom")
        time.sleep(time_sleep)

        # 8) Click “No Timeframe” << to change it when adding a new resource
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/ul/li[4]/a"
        ).click()
        print("✅ No Time Frame link clicked")
        time.sleep(time_sleep)

        # 9) Click “Add a Resource”
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/div[1]/a"
        ).click()
        print("✅ Add a Resource link clicked")
        time.sleep(time_sleep)

        # 10) Select “Link” checkbox
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div/label[6]"
        ).click()
        print("✅ Link checkbox selected")
        time.sleep(time_sleep)

        # 11) Three “Next Step” clicks with intermediate checkboxes
        # → Next (then “Optional”)
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        ).click()
        time.sleep(time_sleep)
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]"
        ).click()
        time.sleep(time_sleep)

        # → Next (then “Hide this resource”)
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        ).click()
        time.sleep(time_sleep)
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[2]"
        ).click()
        time.sleep(time_sleep)

        # → Final Next
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        ).click()
        time.sleep(time_sleep)

        # 12) Enter Monitor URL "Please provide the full URL of the link"
        url_input = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/div/input"
        )
        # clear the existing pre-filled value
        url_input.clear()
        # now type in your new URL
        dramatic_input(url_input, monitor_url)
        time.sleep(time_sleep)

        # 13) Enter Lesson Title "You can optionally provide a different title for this link"
        title_input = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/div/input"
        )
        dramatic_input(title_input, monitor_title)
        time.sleep(time_sleep)
        
        # scroll instantly to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 14) Enter Lesson Description "Please provide a description for this link"
        # 1) Locate the editor iframe and switch into it
        iframe = driver.find_element(
            By.CSS_SELECTOR,
            "#cke_event-resource-link-description iframe.cke_wysiwyg_frame"
        )
        driver.switch_to.frame(iframe)

        # 2) Now target the editable <body> inside the iframe
        editor_body = driver.find_element(
            By.CSS_SELECTOR,
            "body[contenteditable='true']"
        )

        # 3) Clear any existing content
        #    Option A: .clear()
        try:
            editor_body.clear()
        except:
            # Option B: select all + delete
            editor_body.send_keys(Keys.COMMAND + "a", Keys.DELETE)

        # 4) Type your new description
        dramatic_input(editor_body, monitor_title)

        # 5) Switch back to the main document
        driver.switch_to.default_content()
        print("✅ Description added")

        # 15) Save Resource
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        ).click()
        time.sleep(time_sleep)
        
        # 16) Close or Attach another Resource
        driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]"
        ).click()
        time.sleep(time_sleep)
        """
        """
        print("✅ Resource added successfully for⬇️")
        print("   LAMS Lesson Title : "+ monitor_title)
        print("   Elentra Event URL : "+ elentra_url)
        print("   LAMS Student URL  : "+ "WIP")  
        print("   LAMS Monitor URL  : "+ monitor_url)

    except Exception as e:
        print("❌ Resource not added successfully:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()

