import os
import sys
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import RETRY_LIMIT, HEADLESS, LOGIN_URL

def load_credentials():
    try:
        with open("config/credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Credentials file not found at config/credentials.json")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in credentials file")
        sys.exit(1)

def create_driver():
    # Load Chrome profile settings
    try:
        with open("config/chrome_config.json", "r") as f:
            chrome_config = json.load(f)
    except FileNotFoundError:
        logger.error("Chrome config file not found at config/chrome_config.json")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Chrome config file")
        sys.exit(1)

    options = webdriver.ChromeOptions()

    # Kill all existing Chrome instances first
    try:
        if os.name == 'nt':  # Windows
            os.system("taskkill /f /im chrome.exe >nul 2>&1")
            os.system("taskkill /f /im chromedriver.exe >nul 2>&1")
        else:  # Linux/Mac
            os.system("pkill -f chrome")
            os.system("pkill -f chromedriver")
        time.sleep(2)  # Give time for processes to terminate
        logger.info("Killed existing Chrome processes")
    except Exception as e:
        logger.warning(f"Could not kill Chrome processes: {e}")

    logger.info("Trying Method 3: Using temporary profile with cookies...")

    # Create options for Method 3
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

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

    driver.set_page_load_timeout(30)
    logger.info("Successfully created driver with Method 3")
    return driver

def is_logged_in(driver):
    """Check if we're already logged in to LinkedIn"""
    try:
        # Wait briefly for the page to load
        time.sleep(2)
        
        # Check URL for feed or home indication
        if "feed" in driver.current_url or "/home" in driver.current_url:
            return True
            
        # Alternative: Look for elements that would only be present when logged in
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'global-nav')]"))
            )
            return True
        except TimeoutException:
            pass
            
        # Check for the login button which would indicate NOT logged in
        try:
            driver.find_element(By.XPATH, "//a[contains(@class, 'nav__button-secondary') or contains(@href, '/login')]")
            return False
        except NoSuchElementException:
            # If login button is not found, we might be logged in
            pass
            
        # Final check for profile menu
        try:
            driver.find_element(By.XPATH, "//div[contains(@class, 'global-nav__me-photo')]")
            return True
        except NoSuchElementException:
            return False
            
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return False

def login_linkedin(driver, username, password):
    """Log in to LinkedIn"""
    logger.info("Attempting to access LinkedIn...")
    
    # Navigate directly to LinkedIn homepage
    try:
        driver.get("https://www.linkedin.com/")
        logger.info("Successfully loaded LinkedIn homepage")
    except Exception as e:
        logger.error(f"Failed to load LinkedIn homepage: {e}")
        return False
    
    time.sleep(3)
    
    # Check if we're already logged in
    if is_logged_in(driver):
        logger.info("Already logged in to LinkedIn!")
        return True
    
    # Extract cookies from original profile (if this is Method 3 and cookies can be accessed)
    try:
        cookie_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "config", "linkedin_cookies.json")
        if os.path.exists(cookie_file):
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                
            logger.info(f"Loading {len(cookies)} saved cookies")
            for cookie in cookies:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.warning(f"Could not add cookie: {e}")
            
            # Refresh the page after adding cookies
            driver.refresh()
            time.sleep(3)
            
            # Check if we're logged in after adding cookies
            if is_logged_in(driver):
                logger.info("Login successful via cookies!")
                return True
    except Exception as e:
        logger.warning(f"Error loading cookies: {e}")
    
    # If not logged in, proceed with manual login
    try:
        logger.info(f"Navigating to login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        time.sleep(3)

        # Wait for login form elements to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        except TimeoutException:
            logger.warning("Login form not found, trying to click sign in button first")
            try:
                # Look for and click "Sign in" button if on homepage
                sign_in_buttons = driver.find_elements(By.XPATH, "//a[contains(@class, 'nav__button-secondary') or text()='Sign in']")
                if sign_in_buttons:
                    sign_in_buttons[0].click()
                    time.sleep(2)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "username"))
                    )
            except Exception as e:
                logger.error(f"Could not find sign-in button: {e}")
                return False
        
        user_input = driver.find_element(By.ID, "username")
        pass_input = driver.find_element(By.ID, "password")
        
        # Clear fields first
        user_input.clear()
        pass_input.clear()
        
        # Type slowly to mimic human behavior
        for char in username:
            user_input.send_keys(char)
            time.sleep(0.05)
        
        for char in password:
            pass_input.send_keys(char)
            time.sleep(0.05)
        
        # Find and click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Verify login success
        if is_logged_in(driver):
            logger.info("Login successful!")
            
            # Save cookies for future use
            try:
                cookies = driver.get_cookies()
                cookie_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         "config", "linkedin_cookies.json")
                with open(cookie_file, 'w') as f:
                    json.dump(cookies, f)
                logger.info(f"Saved {len(cookies)} cookies for future use")
            except Exception as e:
                logger.warning(f"Could not save cookies: {e}")
                
            return True
        else:
            logger.error("Login failed - not redirected to feed page")
            # Capture screenshot for debugging
            try:
                driver.save_screenshot("login_failed.png")
                logger.info("Screenshot saved as login_failed.png")
            except:
                pass
            return False
            
    except NoSuchElementException as e:
        logger.error(f"Login elements not found: {e}")
        return False
    except TimeoutException:
        logger.error("Timed out waiting for login elements")
        return False
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return False

def start_login_process():
    creds = load_credentials()
    success = False
    attempts = 0
    driver = None

    while not success and attempts < RETRY_LIMIT:
        try:
            logger.info(f"Login attempt {attempts + 1}/{RETRY_LIMIT}")
            
            if driver:
                driver.quit()
                
            driver = create_driver()
            success = login_linkedin(driver, creds["username"], creds["password"])
            
            if success:
                logger.info("Successfully logged in to LinkedIn")
                
                # Optional: Wait a bit before proceeding
                time.sleep(3)
                
                # After successful login, start the connection process
                try:
                    from automation.connection_requester import process_connections
                    logger.info("Starting connection requests process")
                    process_connections(driver, max_requests=5)
                except ImportError:
                    logger.error("Could not import process_connections module")
                except Exception as e:
                    logger.error(f"Error in process_connections: {e}")
            else:
                logger.warning("Login unsuccessful")
                
        except WebDriverException as e:
            logger.error(f"WebDriver issue: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            if not success:
                logger.info(f"Retrying... ({attempts + 1}/{RETRY_LIMIT})")
                attempts += 1
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                # Wait before retrying
                time.sleep(5)
            else:
                break

    if not success:
        logger.error(f"Failed to log in after {RETRY_LIMIT} attempts")
    
    # Cleanup
    if driver:
        try:
            driver.quit()
        except:
            pass
            
    return success

def scroll_and_collect_profiles(driver, max_profiles=10):
    """
    Scrolls through the search results page and collects profile information.
    
    Args:
        driver: Selenium WebDriver instance
        max_profiles: Maximum number of profiles to collect
        
    Returns:
        List of dictionaries containing profile information
    """
    logger.info(f"Collecting up to {max_profiles} profiles...")
    
    profiles = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(profiles) < max_profiles:
        # Find all profile cards
        try:
            profile_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'reusable-search__result-container')]"))
            )
            
            for card in profile_cards:
                if len(profiles) >= max_profiles:
                    break
                    
                try:
                    # Extract profile information
                    name_element = card.find_element(By.XPATH, ".//span[@class='entity-result__title-text']//a")
                    name = name_element.text.strip()
                    url = name_element.get_attribute("href")
                    
                    # Try to get headline
                    try:
                        headline = card.find_element(By.XPATH, ".//div[@class='entity-result__primary-subtitle']").text.strip()
                    except:
                        headline = "No headline available"
                    
                    # Check if we already have this profile
                    if not any(p["url"] == url for p in profiles):
                        profiles.append({
                            "name": name,
                            "headline": headline,
                            "url": url
                        })
                        logger.info(f"Collected profile: {name}")
                except Exception as e:
                    logger.warning(f"Error collecting profile: {str(e)}")
                    continue
        except TimeoutException:
            logger.warning("Timed out waiting for profile cards")
            break
        except Exception as e:
            logger.warning(f"Error finding profile cards: {str(e)}")
            break
        
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try one more scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("Reached end of page")
                break
                
        last_height = new_height
    
    logger.info(f"Collected {len(profiles)} profiles")
    return profiles

# Entry point
if __name__ == "__main__":
    start_login_process()