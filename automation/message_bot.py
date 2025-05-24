import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import os

def remove_non_bmp_characters(text):
    """Remove non-BMP Unicode characters from the given text."""
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

def open_messaging_page(driver):
    """Navigate to LinkedIn messaging page."""
    driver.get("https://www.linkedin.com/messaging/")
    time.sleep(5)

def get_recent_conversations(driver, max_contacts=5):
    """Get recent conversation threads from the messaging page."""
    try:
        # Updated XPath to match the provided HTML structure
        threads = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'msg-conversation-listitem__link')]"))
        )
        contacts = []
        for thread in threads[:max_contacts]:
            try:
                name_elem = thread.find_element(By.XPATH, ".//h3[contains(@class, 'msg-conversation-listitem__participant-names')]//span")
                name = name_elem.text.strip()
                if name:
                    contacts.append((name, thread))
            except:
                continue
        return contacts
    except Exception as e:
        return []

def refresh_thread(driver, name):
    """Attempt to re-fetch the conversation thread for the given name."""
    try:
        threads = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'msg-conversation-listitem__link')]"))
        )
        for thread in threads:
            try:
                name_elem = thread.find_element(By.XPATH, ".//h3[contains(@class, 'msg-conversation-listitem__participant-names')]//span")
                if name_elem.text.strip() == name:
                    return thread
            except:
                continue
        return None
    except:
        return None

def send_message(driver, thread, name, message, log_callback=lambda msg, level="info": None, resume_path=None):
    """Send a message to a contact via their conversation thread."""
    try:
        # Attempt to click the conversation thread with retries
        current_thread = thread
        for attempt in range(3):
            try:
                log_callback(f"Clicking conversation thread for {name} (attempt {attempt+1})", level="debug")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_thread)
                time.sleep(1)
                current_thread.click()
                break
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                log_callback(f"Click attempt {attempt+1} failed: {str(e)}", level="debug")
                if attempt < 2:
                    # Try to refresh the thread
                    log_callback(f"Attempting to refresh thread for {name}", level="debug")
                    current_thread = refresh_thread(driver, name)
                    if not current_thread:
                        log_callback(f"Could not refresh thread for {name}", level="debug")
                        break
                    time.sleep(1)
                else:
                    log_callback(f"Failed to click conversation thread after {attempt+1} attempts", level="user")
                    return False
        
        if not current_thread:
            log_callback(f"Failed to locate conversation thread for {name}", level="user")
            return False
        
        # Wait for the conversation to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'msg-conversation-card__content')]"))
        )
        time.sleep(3)  # Increased wait for stability
        
        # Find the message input box
        message_box_xpaths = [
            "//div[contains(@class, 'msg-form__contenteditable') and @role='textbox']",
            "//div[contains(@class, 'msg-form__message-texteditor')]//div[@role='textbox']",
            "//div[contains(@class, 'public-DraftEditor-content')][@role='textbox']"
        ]
        
        message_box = None
        for xpath in message_box_xpaths:
            try:
                message_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                if message_box:
                    break
            except:
                continue
        
        if not message_box:
            log_callback("Message input box not found", level="user")
            return False
            
        # Clear any existing text and focus
        driver.execute_script("arguments[0].innerHTML = '';", message_box)
        driver.execute_script("arguments[0].focus();", message_box)
        time.sleep(1)
        
        # Send the message
        clean_message = remove_non_bmp_characters(message)
        message_box.send_keys(clean_message)
        time.sleep(1)
        
        # Attach resume if provided
        if resume_path and os.path.exists(resume_path):
            try:
                attach_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Attach')]"))
                )
                attach_button.click()
                time.sleep(1)
                
                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(os.path.abspath(resume_path))
                log_callback("Resume attached", level="info")
                time.sleep(2)
            except Exception as e:
                log_callback(f"Failed to attach resume: {str(e)}", level="user")
        
        # Try multiple methods to send the message
        send_success = False
        
        # Method 1: Direct CSS selector for the send button
        try:
            send_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            log_callback("Message sent via direct CSS selector", level="info")
            send_success = True
        except Exception as e:
            log_callback(f"CSS selector method failed: {str(e)}", level="debug")
        
        # Method 2: Try XPath if CSS selector failed
        if not send_success:
            send_button_xpaths = [
                "//button[contains(@class, 'msg-form__send-button')]",
                "//div[contains(@class, 'msg-form__right-actions')]//button[text()='Send']",
                "//footer//button[text()='Send']"
            ]
            
            for xpath in send_button_xpaths:
                try:
                    send_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    driver.execute_script("arguments[0].click();", send_button)
                    log_callback("Message sent via XPath method", level="info")
                    send_success = True
                    break
                except:
                    continue
            
            if not send_success:
                log_callback("XPath methods failed", level="debug")
        
        # Method 3: Try keyboard shortcuts as a fallback
        if not send_success:
            try:
                log_callback("Trying keyboard shortcuts...", level="debug")
                message_box.send_keys(Keys.RETURN)
                log_callback("Message sent using keyboard shortcut", level="info")
                send_success = True
            except Exception as e:
                log_callback(f"Keyboard shortcut failed: {str(e)}", level="debug")
        
        if not send_success:
            log_callback("All send methods failed. Message may not have been sent.", level="user")
            return False
            
        time.sleep(2)
        log_callback(f"Message successfully sent to {name}", level="user")
        return True
        
    except Exception as e:
        log_callback(f"Failed to send message to {name}: {str(e)}", level="user")
        return False

def start_bulk_messaging(driver, contacts, message, log_callback=lambda msg, level="info": None, resume_path=None):
    """Send bulk messages to a list of contacts."""
    log_callback("Starting bulk messaging process...", level="user")
    for name, thread in contacts:
        try:
            log_callback(f"Messaging contact: {name}", level="user")
            success = send_message(driver, thread, name, message, log_callback=log_callback, resume_path=resume_path)
            if success:
                log_callback(f"Message sent to {name}", level="user")
            else:
                log_callback(f"Failed to send message to {name}", level="user")
            time.sleep(3)
        except Exception as e:
            log_callback(f"Error messaging {name}: {str(e)}", level="user")
    log_callback("Bulk messaging completed", level="user")