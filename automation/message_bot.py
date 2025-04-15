import time
from selenium.webdriver.common.by import By
from ai.ai_generator import generate_connection_message
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import unicodedata

def remove_non_bmp_characters(text):
    """Remove non-BMP Unicode characters from the given text."""
    return ''.join(char for char in text if ord(char) <= 0xFFFF)


def open_messaging_page(driver):
    driver.get("https://www.linkedin.com/messaging/")
    time.sleep(5)
    print("💬 Opened LinkedIn Messaging page.")

def get_recent_conversations(driver, max_contacts=5):
    threads = driver.find_elements(By.XPATH, "//li[contains(@class, 'msg-conversations-container__convo-item')]")
    contacts = []

    for thread in threads[:max_contacts]:
        try:
            name_elem = thread.find_element(By.CLASS_NAME, "msg-conversation-listitem__participant-names")
            name = name_elem.text.strip()
            contacts.append((name, thread))
        except:
            continue

    return contacts

def select_message_target(driver):
    choice = input("📢 Do you want to:\n1. Broadcast to recent contacts\n2. Pick specific contacts\nEnter 1 or 2: ").strip()
    return choice


def send_message(driver, thread, message):
    try:
        # Open the conversation thread with retries
        for attempt in range(3):
            try:
                thread.click()
                break
            except (ElementClickInterceptedException, StaleElementReferenceException):
                print(f"⚠️ Click attempt {attempt+1} failed, retrying...")
                time.sleep(1)
                if attempt == 2:
                    driver.execute_script("arguments[0].click();", thread)
        
        # Wait for the conversation to load
        time.sleep(3)
        
        # Find the message box
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
            raise Exception("Message input box not found")
            
        # Clear any existing text and focus
        driver.execute_script("arguments[0].innerHTML = '';", message_box)
        driver.execute_script("arguments[0].focus();", message_box)
        time.sleep(1)
        
        # Send the entire message at once
        message_box.send_keys(message)
        time.sleep(1)
        
        # Try multiple methods to send the message
        send_success = False
        
        # METHOD 1: Direct CSS selector for the send button (most reliable based on your HTML)
        try:
            send_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            print("✅ Message sent via direct CSS selector.")
            send_success = True
        except Exception as e:
            print(f"⚠️ CSS selector method failed: {str(e)}")
        
        # METHOD 2: Try using XPath if CSS selector failed
        if not send_success:
            try:
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
                        print("✅ Message sent via XPath method.")
                        send_success = True
                        break
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ XPath methods failed: {str(e)}")
        
        # METHOD 3: Try clicking the send toggle options button and then pressing Enter
        if not send_success:
            try:
                print("⚠️ Trying send toggle options method...")
                toggle_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-toggle"))
                )
                toggle_button.click()
                time.sleep(1)
                
                # After opening the toggle, press Enter - this often works
                message_box.send_keys(Keys.CONTROL + Keys.RETURN)
                send_success = True
                print("✅ Message sent using toggle + keyboard shortcut.")
            except Exception as e:
                print(f"⚠️ Toggle method failed: {str(e)}")
        
        # METHOD 4: Final fallback - try keyboard shortcuts
        if not send_success:
            try:
                print("⚠️ Trying keyboard shortcuts...")
                # Try Shift+Enter
                message_box.send_keys(Keys.SHIFT + Keys.RETURN)
                time.sleep(0.5)
                
                # Try Ctrl+Enter
                message_box.send_keys(Keys.CONTROL + Keys.RETURN)
                time.sleep(0.5)
                
                # Try plain Enter
                message_box.send_keys(Keys.RETURN)
                
                print("✅ Message attempted using keyboard shortcuts.")
                send_success = True
            except Exception as e:
                print(f"⚠️ Keyboard shortcuts failed: {str(e)}")
        
        if not send_success:
            print("❌ All send methods failed. Message may not have been sent.")
            
        # Wait a moment before proceeding
        time.sleep(2)
            
    except Exception as e:
        print(f"❌ Failed to send message: {str(e)}")
        print("⚠️ Moving to next contact...")
        

def message_contacts(driver, contacts):
    for name, thread in contacts:
        print("\n👤 Contact:", name)
        prompt = f"Write a short, friendly follow-up message to {name} on LinkedIn."
        ai_msg = generate_connection_message(prompt)

        print("💬 Suggested message:\n", ai_msg)

        action = input("🤖 Send this message? [y = yes / e = edit / s = skip]: ").strip().lower()
        if action == "y":
            send_message(driver, thread, ai_msg)
        elif action == "e":
            custom_msg = input("✍️ Enter your custom message: ").strip()
            send_message(driver, thread, custom_msg)
        else:
            print("⏭️ Skipped.")

def start_bulk_messaging(driver):
    open_messaging_page(driver)

    contacts = get_recent_conversations(driver)
    print(f"📬 Found {len(contacts)} recent chats.")

    if not contacts:
        print("⚠️ No recent chats found.")
        return

    choice = select_message_target(driver)

    if choice == "1":
        message_contacts(driver, contacts)
    elif choice == "2":
        for idx, (name, _) in enumerate(contacts):
            print(f"{idx+1}. {name}")
        selected = input("Enter contact numbers (comma-separated): ").strip().split(",")

        selected_indices = [int(i)-1 for i in selected if i.strip().isdigit()]
        selected_contacts = [contacts[i] for i in selected_indices if i < len(contacts)]

        message_contacts(driver, selected_contacts)
    else:
        print("❌ Invalid option.")