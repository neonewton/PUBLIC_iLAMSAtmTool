# Test Case

# 1) Open Web Browser (Chrome/firefox/Edge).
# 2) Open URL https://opensource-demo.orangehrmlive.com/
# 3) Enter username (Admin).
# 4) Enter password (admin123).
# 5) Click on Login.
# 6) Capture title of the home page. (Actual title)
# 7) Verify title of the page: OrangeHRM (Expected)
# 8) close browser

import sys
print(sys.executable)

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Specify the path to the Edge WebDriver (use the correct macOS path)
edge_driver_path = '/Users/neltontan/Driver/edgedriver_mac64_m1/msedgedriver'

# Create a Service object
service = Service(executable_path=edge_driver_path)

# Pass the Service object to the Edge WebDriver
driver = webdriver.Edge(service=service)

# Open the target URL
driver.get("https://opensource-demo.orangehrmlive.com/")

# Wait for the username input to be visible and interactable
WebDriverWait(driver, 100).until(
    EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div[2]/input"))
)

# Find and interact with the login elements
driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[1]/div/div[2]/div[2]/form/div[1]/div/div[2]/input").send_keys("Admin")
driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[1]/div/div[2]/div[2]/form/div[2]/div/div[2]/input").send_keys("admin123")
driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/div[1]/div/div[2]/div[2]/form/div[3]/button").click()

# If you're trying to click a button, ensure the XPath is correctly written
# Example (assuming the XPath is correct):
# driver.find_element(By.XPATH, "//*[@id='app']/div[1]/div/div[1]/div/div[2]/div[2]/form/div[3]/button").click()

# Verify if login is successful

act_title = driver.title
exp_title = "OrangeHRM"

if act_title == exp_title:
    print("Login Test passed")
else:
    print("Login Test failed")

# Close the driver
driver.close()