import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Load credentials
with open('config/credentials.json') as f:
    creds = json.load(f)

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login")

# Login steps
driver.find_element(By.ID, "username").send_keys(creds['username'])
driver.find_element(By.ID, "password").send_keys(creds['password'])
driver.find_element(By.XPATH, "//button[@type='submit']").click()

time.sleep(5)  # Let page load
print("✅ Login attempted.")
driver.quit()
