# automation/message_bot.py (updated)
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import os

def remove_non_bmp_characters(text):
    """Remove non-BMP Unicode characters from the given text."""
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

def open_messaging_page(driver, max_retries=3):
    """Open LinkedIn Messaging page (either inbox or thread) and ensure the conversation list loads."""
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"[DEBUG] Attempt {attempt + 1}: Opening messaging page...")
            driver.get("https://www.linkedin.com/messaging/")

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            if "/messaging/thread/" in driver.current_url:
                print(f"[DEBUG] On thread page: {driver.current_url}, proceeding to extract contacts from sidebar")

            inbox_loaded = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.msg-conversations-container__conversations-list"))
            )

            print(f"[DEBUG] Final URL before returning: {driver.current_url}")
            if inbox_loaded:
                print("[DEBUG] Successfully loaded messaging page with conversation list.")
                return True

        except TimeoutException as e:
            print(f"[DEBUG] Conversation list did not load properly: {str(e)}. Retrying...")
            attempt += 1
            time.sleep(1)

    raise Exception("Failed to load messaging page with conversation list after multiple attempts.")

def get_contacts(driver):
    try:
        if "messaging" not in driver.current_url:
            open_messaging_page(driver)
        else:
            print("[DEBUG] Already on messaging page, skipping open_messaging_page call.")

        print(f"[DEBUG] Current URL before scraping contacts: {driver.current_url}")

        thread_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.msg-conversation-listitem__link"))
        )

        seen_names = set()
        contacts = []

        for element in thread_elements:
            try:
                name = None
                try:
                    name = element.find_element(By.CSS_SELECTOR, "h3.msg-conversation-card__participant-names span.truncate").text.strip()
                except NoSuchElementException:
                    print("[DEBUG] Skipping contact: Could not find name element")
                    continue

                if not name:
                    print("[DEBUG] Skipping contact: Name is empty")
                    continue

                if element.find_elements(By.XPATH, "./ancestor::li[contains(@class, 'msg-conversation-listitem')]//span[contains(@class, 'msg-conversation-card__pill')]"):
                    print(f"[DEBUG] Skipping sponsored message for {name}")
                    continue

                if name not in seen_names:
                    seen_names.add(name)
                    contacts.append((name, element))
                    print(f"[DEBUG] Added contact: {name}")
                else:
                    print(f"[DEBUG] Skipping duplicate contact: {name}")

            except Exception as e:
                print(f"[DEBUG] Error extracting contact: {str(e)}")
                continue

        print(f"[DEBUG] Found {len(contacts)} valid contacts")
        return contacts

    except Exception as e:
        print(f"[ERROR] Failed to retrieve contacts: {str(e)}")
        print(f"[DEBUG] Current URL: {driver.current_url}")
        print(f"[DEBUG] Page source snippet: {driver.page_source[:500]}...")
        return []

def refresh_thread(driver, name):
    """Attempt to re-fetch the conversation thread for the given name."""
    try:
        threads = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.msg-conversation-listitem__link"))
        )
        for thread in threads:
            try:
                name_elem = thread.find_element(By.CSS_SELECTOR, "h3.msg-conversation-card__participant-names span.truncate")
                if name_elem.text.strip() == name:
                    return thread
            except:
                continue
        return None
    except:
        return None

def send_message(driver, name, thread_element, message, resume_path, log_callback=print):
    try:
        log_callback(f"[debug] Sending message to {name}", level="debug")

        if "messaging" not in driver.current_url:
            open_messaging_page(driver)

        log_callback(f"[debug] Current URL before locating thread: {driver.current_url}", level="debug")

        attempt = 1
        max_attempts = 3
        current_thread = thread_element

        while attempt <= max_attempts:
            try:
                log_callback(f"[debug] Clicking conversation thread for {name} (attempt {attempt})", level="debug")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_thread)
                time.sleep(1)
                current_thread.click()
                break
            except (StaleElementReferenceException, NoSuchElementException) as e:
                if attempt == max_attempts:
                    raise Exception(f"Failed to click thread for {name}: {str(e)}")
                log_callback(f"[debug] Click attempt {attempt} failed: {str(e)}, refreshing thread", level="debug")
                current_thread = refresh_thread(driver, name)
                if not current_thread:
                    raise Exception(f"Could not refresh thread for {name}")
                attempt += 1
                time.sleep(2)

        message_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
        )
        message_input.send_keys(message)

        if resume_path and os.path.exists(resume_path):
            try:
                log_callback(f"[debug] Attaching resume: {resume_path}", level="debug")
                attach_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Attach a file to your conversation with')]"))
                )
                attach_button.click()
                time.sleep(1)

                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(os.path.abspath(resume_path))
                log_callback("Resume attached successfully", level="info")
                time.sleep(2)  # Short delay to ensure LinkedIn processes the upload

            except Exception as e:
                log_callback(f"Failed to attach resume: {str(e)}", level="user")
                raise

        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
        )
        send_button.click()

        time.sleep(2)
        log_callback(f"[debug] Message sent successfully to {name}", level="debug")
        return True

    except Exception as e:
        log_callback(f"[user] Failed to send message to {name}: {str(e)}", level="user")
        return False

def start_bulk_messaging(driver, contacts, message_template, log_callback=lambda msg, level="info": None, resume_path=None):
    """Send messages to a list of contacts, replacing [recipient] with the contact's name."""
    print(f"[DEBUG] Type of log_callback in start_bulk_messaging: {type(log_callback)}")
    
    if not callable(log_callback):
        def default_log(msg, level="info"):
            print(f"[FALLBACK LOG] [{level}] {msg}")
        log_callback = default_log
        log_callback(f"Warning: log_callback was not callable, using default logger", level="user")

    for name, thread in contacts:
        print(f"[DEBUG] Type of name: {type(name)}")
        print(f"[DEBUG] Type of thread: {type(thread)}")
        log_callback(f"Messaging contact: {name}", level="user")
        
        # Replace [recipient] placeholder with the contact's name
        message = message_template.replace("[recipient]", name)
        log_callback(f"[debug] Message content after replacement: {message}", level="debug")
        
        success = send_message(driver, name, thread, message, resume_path, log_callback=log_callback)
        if success:
            log_callback(f"Message sent to {name}", level="user")
        else:
            log_callback(f"Failed to send message to {name}", level="user")
        time.sleep(2)