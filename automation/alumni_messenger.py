import os
import time
import json
import sys


# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ai.ai_generator import generate_alumni_message
from automation.message_bot import send_message_to_profile
from utils.logger import log_action

LOG_FILE = "logs/sent_alumni.json"

def has_already_messaged(profile_url):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, "r") as f:
        data = json.load(f)
        return profile_url in data.get("sent", [])

def log_alumni_message(profile_url):
    data = {"sent": []}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    data["sent"].append(profile_url)
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def navigate_to_alumni_page(driver, college_name):
    driver.get("https://www.linkedin.com/school/")
    time.sleep(2)

    search_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Search')]"))
    )
    search_input.send_keys(college_name)
    search_input.send_keys(Keys.RETURN)
    time.sleep(3)

    try:
        school_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/school/') and contains(@href, 'linkedin.com/school')]"))
        )
        school_link.click()
        time.sleep(3)
    except Exception as e:
        print(f"[❌] Could not open school page: {e}")
        return False

    try:
        alumni_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/alumni/')]"))
        )
        driver.execute_script("arguments[0].click();", alumni_link)
        print("✅ Navigated to alumni page.")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[❌] Could not open alumni section: {e}")
        return False

def extract_alumni_profiles(driver, max_profiles=5):
    profiles = []
    time.sleep(2)
    scroll_area = driver.find_element(By.TAG_NAME, "body")

    for _ in range(3):
        scroll_area.send_keys(Keys.END)
        time.sleep(2)

    cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'entity-result__item')]")[:max_profiles]
    for card in cards:
        try:
            name_elem = card.find_element(By.XPATH, ".//span[@dir='ltr']")
            profile_link = card.find_element(By.XPATH, ".//a").get_attribute("href")
            headline = card.find_element(By.XPATH, ".//div[contains(@class, 'entity-result__primary-subtitle')]").text.strip()
            profiles.append({
                "name": name_elem.text.strip(),
                "profile_url": profile_link,
                "headline": headline
            })
        except:
            continue
    print(f"🔍 Found {len(profiles)} alumni profiles.")
    return profiles

def extract_college_info(driver):
    try:
        edu_section = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@id, 'education')]"))
        )
        entries = edu_section.find_elements(By.XPATH, ".//li[contains(@class, 'education__list-item')]")
        edu_info = []
        for entry in entries:
            try:
                college = entry.find_element(By.XPATH, ".//h3").text
                degree = entry.find_element(By.XPATH, ".//span[contains(text(), 'Degree')]").text
                year = entry.find_element(By.XPATH, ".//time").text
                edu_info.append((college, degree, year))
            except:
                continue
        return edu_info
    except:
        return []

def message_alumni(driver, college_name, department, graduation_year, resume_path, purpose="connect"):
    if not navigate_to_alumni_page(driver, college_name):
        return

    profiles = extract_alumni_profiles(driver, max_profiles=10)

    for profile in profiles:
        url = profile["profile_url"]
        if has_already_messaged(url):
            print(f"⏭️ Already messaged: {profile['name']} ({url})")
            continue

        driver.get(url)
        time.sleep(5)

        edu_entries = extract_college_info(driver)
        matches = any(college_name.lower() in c.lower() and department.lower() in d.lower()
                      for c, d, y in edu_entries if department)

        if not matches:
            print(f"❌ Skipping {profile['name']} – no matching college/department.")
            continue

        message = generate_alumni_message(profile["name"], college_name, department, graduation_year, purpose)

        success = send_message_to_profile(driver, url, message, resume_path)
        if success:
            log_alumni_message(url)
            log_action("AlumniMessageSent", profile["name"], url)
            print(f"✅ Messaged: {profile['name']}")
        else:
            print(f"❌ Failed to message: {profile['name']}")
