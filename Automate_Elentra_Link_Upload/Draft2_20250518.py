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

def highlight(el, duration=2, color='clear', border="4px solid red"):
    # 1) Scroll the element into view
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    # 2) Save its current style so we can restore later
    original_style = el.get_attribute("style") or ""
    # 3) Overwrite with our highlight style
    highlight_style = f"background: {color} !important; border: {border} !important; {original_style}"
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", el, highlight_style)
    # 4) Pause so you can actually *see* it
    time.sleep(duration)
    # 5) Restore original style
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", el, original_style)

def main():
    time_sleep = 1.5

    # 1) Prompt for IDs
    """
    elentra_event_id = input("Enter Elentra event ID: ").strip()
    lams_lesson_id   = input("Enter LAMS lesson ID: ").strip()
    monitor_title = input("Enter Monitor title: ").strip()
    """
    elentra_event_id = "1696"
    lams_lesson_id = "37655"
    lams_lesson_title = "(test)FM_MiniQuiz_WomanHealth_DDMMYY"
    
    print("✅ ID input")

    # 2) Build URLs & Title
    elentra_event_name = f"{elentra_event_id}"
    elentra_event_url   = f"https://ntu.elentra.cloud/events?id={elentra_event_id}"
    
    lams_monitor_title = f"LAMS {lams_lesson_title} (Facilitator/CE)"
    lams_monitor_url   = f"https://ilams.lamsinternational.com/lams/monitoring/monitoring/monitorLesson.do?lessonID={lams_lesson_id}"
    
    lams_student_title = f"LAMS {lams_lesson_title}"
    lams_student_url   = f"https://ilams.lamsinternational.com/lams/home/learner.do?lessonID={lams_lesson_id}"
    #print(lams_monitor_title)
    #print(lams_student_title)

    print("✅ URL input")
    
    # 3) Setup Chrome WebDriver to attach to existing debug session
    chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
    service = Service(executable_path=chrome_driver_path)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    global driver
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Chrome WebDriver started")
    
    try:
        
        # 4) Navigate to Elentra Event Page
        driver.get(elentra_event_url)
        print("✅ Navigated to Elentra event page")
        time.sleep(time_sleep)

        # 5) Wait for the Administrator checkbox link to be clickable, then click
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[2]/div[2]/div[3]/div[2]/ul/li[2]/a/span"
        )
        highlight(btn)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "/html/body/div[1]/div/div[2]/div[2]/div[3]/div[2]/ul/li[2]/a/span"
            ))
        ).click()
        print("✅ Administrator checkbox clicked")

        # 6) Click “Content”
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[2]/ul/li[2]/a"
        )
        highlight(btn)
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

        # 8) Click “No Timeframe”
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/ul/li[4]/a"
        )
        highlight(btn)
        btn.click()
        print("✅ No Time Frame link clicked")
        time.sleep(time_sleep)

        print("⏳ Inserting Monitor Title now ⏳")
        
        # 9) Click “Add a Resource”
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[3]/div[1]/a"
        )
        highlight(btn)
        btn.click()
        print("✅ Add a Resource link clicked")
        time.sleep(time_sleep)

        # 10) Select “Link” checkbox
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div/label[6]"
        )
        highlight(btn)
        btn.click()
        print("✅ Link checkbox selected")
        time.sleep(time_sleep)

        # 11) Three “Next Step” clicks with intermediate checkboxes
        # → Next (then “Optional”)
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[1]/label[1]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)

        # → Next (then “Hide this resource”)
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/label[2]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)

        # → Final Next
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)

        # 12) Enter Monitor URL
        url_input = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[2]/div/input"
        )
        highlight(url_input)
        url_input.clear()
        dramatic_input(url_input, lams_monitor_url)
        time.sleep(time_sleep)

        # 13) Enter Lesson Title
        title_input = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[2]/form/div[2]/div[3]/div/input"
        )
        highlight(title_input)
        dramatic_input(title_input, lams_monitor_title)
        time.sleep(time_sleep)
        
        # scroll instantly to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 14) Enter Lesson Description
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
        try:
            editor_body.clear()
        except:
            editor_body.send_keys(Keys.COMMAND + "a", Keys.DELETE)

        # 4) Type your new description
        dramatic_input(editor_body, lams_lesson_title)

        # 5) Switch back to the main document
        driver.switch_to.default_content()
        print("✅ Description added")

        # 15) Save Resource
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[3]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)
        
        # 16) Close or Attach another Resource
        btn = driver.find_element(By.XPATH,
            "/html/body/div[1]/div/div[3]/div/div[7]/div[1]/div[6]/div/div/div/div[3]/button[1]"
        )
        highlight(btn)
        btn.click()
        time.sleep(time_sleep)
        
        print("✅ Resource added successfully for⬇️")
        print("   Elentra Lesson Title  : "+ elentra_event_name)
        print("   Elentra Event URL  : "+ elentra_event_url)
        
        print("   LAMS Monitor Title : "+ lams_monitor_title)
        print("   LAMS Monitor URL   : "+ lams_monitor_url)

        #try
        print("⏳ Inserting Student Title now ⏳")
        print("✅ Resource added successfully for⬇️")
        print("   LAMS Student Title : "+ lams_student_title)
        print("   LAMS Student URL   : "+ lams_student_url)

    except Exception as e:
        print("❌ Resource not added successfully:", e)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
