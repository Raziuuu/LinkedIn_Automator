import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import RETRY_LIMIT, HEADLESS, LOGIN_URL

def load_credentials():
    with open("config/credentials.json", "r") as f:
        return json.load(f)

def create_driver():
    # Load Chrome profile settings
    with open("config/chrome_config.json", "r") as f:
        chrome_config = json.load(f)
    
    options = webdriver.ChromeOptions()

    # Use existing logged-in Chrome profile to avoid detection
    user_data_dir = chrome_config["chrome_profile"]["base_path"]
    profile_dir = chrome_config["chrome_profile"]["profile_name"]
    
    # Use your existing Chrome profile directly
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument(f"profile-directory={profile_dir}")

    # Basic options
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # GPU and rendering options
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-webgl2")
    options.add_argument("--disable-3d-apis")
    
    # Performance options
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Headless mode specific options
    if HEADLESS:
        options.add_argument("--headless=new")  # Use new headless mode
        options.add_argument("--window-size=1366,768")  # Reduced window size for better performance
        options.add_argument("--disable-gpu-sandbox")
        options.add_argument("--disable-accelerated-2d-canvas")
        options.add_argument("--disable-accelerated-jpeg-decoding")
        options.add_argument("--disable-accelerated-mjpeg-decode")
        options.add_argument("--disable-accelerated-video-decode")
        options.add_argument("--disable-accelerated-video-encode")
    
    # Automation options
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Use webdriver_manager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Add anti-detection script
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    
    return driver

def login_linkedin(driver, username, password):
    # Navigate directly to LinkedIn
    driver.get("https://www.linkedin.com/")
    time.sleep(3)
    
    # Check if we're already logged in
    if "feed" in driver.current_url:
        print("[✅] Already logged in!")
        return True
    
    # If not logged in, proceed with login
    driver.get(LOGIN_URL)
    time.sleep(2)

    try:
        user_input = driver.find_element(By.ID, "username")
        pass_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        user_input.send_keys(username)
        pass_input.send_keys(password)
        login_button.click()

        time.sleep(3)

        if "feed" in driver.current_url:
            print("[✅] Login successful!")
            return True
        else:
            print("[❌] Login failed.")
            return False
    except NoSuchElementException:
        print("[⚠️] Login elements not found.")
        return False

def start_login_process():
    creds = load_credentials()
    success = False
    attempts = 0
    driver = None

    while not success and attempts < RETRY_LIMIT:
        try:
            driver = create_driver()
            success = login_linkedin(driver, creds["username"], creds["password"])
            if success:
                # After successful login, start the connection process
                from automation.connection_requester import process_connections
                process_connections(driver, max_requests=5)
        except WebDriverException as e:
            print(f"[ERROR] WebDriver issue: {e}")
        finally:
            if not success:
                print(f"[⏳] Retrying... ({attempts + 1}/{RETRY_LIMIT})")
                attempts += 1
                if driver:
                    driver.quit()
            else:
                break

    if not success:
        print("[💥] Failed to log in after retries.")
    elif driver:
        driver.quit()
    return success

# Entry point
if __name__ == "__main__":
    start_login_process()