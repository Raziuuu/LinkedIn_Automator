import os
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Assuming ai_generator and message_bot are under ai/ and automation/
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


def get_current_university(driver):
    """Try to extract university name from LinkedIn profile"""
    driver.get("https://www.linkedin.com/in/me/ ")
    time.sleep(5)

    try:
        # Wait for education section
        education_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@class, 'education')]"))
        )

        entries = education_section.find_elements(By.XPATH, ".//li[contains(@class, 'education__list-item')]")

        if entries:
            school_name = entries[0].find_element(By.XPATH, ".//h3").text.strip()
            return school_name

    except Exception as e:
        print(f"[❌] Could not extract university from profile: {e}")

    return None


def click_people_filter(driver, max_retries=3):
    """Clicks on the 'People' filter with retry mechanism."""
    people_xpath = "//button[contains(., 'People')]"

    for attempt in range(1, max_retries + 1):
        try:
            people_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, people_xpath))
            )
            people_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, people_xpath))
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", people_button)
            time.sleep(1)

            try:
                people_button.click()
            except:
                driver.execute_script("arguments[0].click();", people_button)

            print("✅ People filter clicked.")
            time.sleep(3)
            return True

        except Exception as e:
            print(f"[⚠️] Attempt {attempt} failed: {e}")
            time.sleep(2)

    print("[❌] Could not click People filter after multiple attempts.")
    return False


def apply_company_filter(driver):
    """Apply company filter by selecting from predefined options shown in UI."""
    try:
        # Step 1: Open Current Company filter
        company_filter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Current company')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", company_filter_button)
        time.sleep(1)
        company_filter_button.click()
        print("✅ Current company filter opened.")
        time.sleep(2)

        # Step 2: Wait for company list
        company_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, 
                "//ul[contains(@class, 'search-reusables__collection-values-container')]//li[contains(@class, 'search-reusables__collection-values-item')]"))
        )

        if not company_items:
            print("[❌] No company options found.")
            return False

        # Step 3: Extract company names
        company_names = []
        for idx, item in enumerate(company_items):
            label = item.find_element(By.XPATH, ".//span[@class='t-14 t-black--light t-normal']")
            name = label.text.strip()
            if name:
                company_names.append(name)
                print(f"{idx + 1}. {name}")

        if not company_names:
            print("[❌] Could not extract any readable company names.")
            return False

        # Step 4: Get user selection
        while True:
            try:
                choice = int(input(f"🔢 Select a company (1-{len(company_names)}): "))
                if 1 <= choice <= len(company_names):
                    selected_name = company_names[choice - 1]
                    break
                else:
                    print(f"[⚠️] Please enter a number between 1 and {len(company_names)}")
            except ValueError:
                print("[⚠️] Invalid input. Please enter a number.")

        print(f"✅ Selected: {selected_name}")

        # Step 5: Find and click checkbox for selected company
        selected_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                f"//label[.//span[text()='{selected_name}']]/preceding-sibling::input[@type='checkbox']"))
        )
        driver.execute_script("arguments[0].click();", selected_item)
        print(f"✅ Checkbox clicked for: {selected_name}")
        time.sleep(2)

        # Step 6: Click "Show Results"
        show_results = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Show results']]"))
        )
        show_results.click()
        print("✅ Applied company filter and showing results.")
        time.sleep(5)
        return True

    except Exception as e:
        print(f"[❌] Error applying company filter: {e}")
        return False

def search_for_university(driver, university_name):
    """Search for university using global search bar"""
    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
        )
        search_input.clear()
        search_input.send_keys(university_name)
        search_input.send_keys(Keys.RETURN)
        print(f"🔍 Searched for university: {university_name}")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[❌] Failed to perform university search: {e}")
        return False

def navigate_to_alumni_page(driver, college_name):
    driver.get("https://www.linkedin.com/school/ ")
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


def extract_alumni_profiles(driver, max_profiles=10):
    profiles = []
    scroll_area = driver.find_element(By.TAG_NAME, "body")

    for _ in range(3):  # Scroll to load more profiles
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
        except Exception as e:
            continue

    print(f"🔍 Found {len(profiles)} alumni profiles.")
    return profiles


def extract_college_info(driver):
    try:
        edu_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@id, 'education')]"))
        )
        entries = edu_section.find_elements(By.XPATH, ".//li[contains(@class, 'education__list-item')]")
        return [entry.text for entry in entries]
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
        matches = any(college_name.lower() in entry.lower() and department.lower() in entry.lower() for entry in edu_entries)

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


def run_alumni_outreach(driver):
    """Main function to handle alumni outreach workflow"""

    # Step 1: Get university
    university = get_current_university(driver)
    if not university:
        university = input("🎓 Could not auto-detect university. Please enter manually: ").strip()

    print(f"🎓 Using university: {university}")

    # Step 2: Search for university
    if not search_for_university(driver, university):
        print("[❌] Failed to search for university. Aborting.")
        return

    # Step 3: Click People filter
    if not click_people_filter(driver):
        print("[⚠️] Could not click People filter. Proceeding without it.")

    # Step 4: Ask for company and apply filter
    company = input("💼 Enter company name (or press Enter to skip): ").strip()
    if company:
        if not apply_company_filter(driver):
            print("[⚠️] Failed to apply company filter. Continuing without it.")

    # Step 5: Gather remaining inputs
    department = input("📚 Enter your department/major: ").strip()
    year = input("📅 Enter your graduation year: ").strip()
    resume_path = input("📄 Enter full path to your resume (PDF): ").strip()
    purpose = input("✉️ Purpose of message (e.g., 'seek guidance', 'network', 'internship help'): ").strip()

    if not os.path.isfile(resume_path):
        print("❌ Invalid resume file path.")
        return

    # Step 6: Start messaging
    message_alumni(driver, university, department, year, resume_path, purpose)