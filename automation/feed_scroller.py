from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import ( TimeoutException, NoSuchElementException, ElementClickInterceptedException, ) 
import time


import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def scroll_slowly(driver, scroll_pause=2, max_scrolls=5): 
    for i in range(max_scrolls): 
        driver.execute_script("window.scrollBy(0, window.innerHeight);") 
        time.sleep(scroll_pause)

def get_post_containers(driver): 
    try: 
        return driver.find_elements(By.XPATH, "//div[contains(@data-urn, 'urn:li:activity')]") 
    except NoSuchElementException: 
        return []

def process_post(driver, post_element, index): 
    print(f"\n👀 Post #{index + 1}")

    try:
        # Scroll the post into view
        driver.execute_script("arguments[0].scrollIntoView(true);", post_element)
        time.sleep(2)  # Wait for the post to stabilize
    
        # Try finding action buttons (like/comment)
        action_buttons = post_element.find_elements(
            By.XPATH, ".//button[contains(@aria-label, 'Like') or contains(@aria-label, 'Comment')]"
        )
    
        action = input("💬 Action? [like / comment / skip]: ").strip().lower()
        
        if action == "like":
            for btn in action_buttons:
                label = btn.get_attribute("aria-label")
                if "Like" in label:
                    btn.click()
                    print("👍 Liked.")
                    break
        
        elif action == "comment":
            try:
                # Find and click the comment button using multiple locators
                comment_button = None
                retries = 3
                for attempt in range(retries):
                    try:
                        comment_button = post_element.find_element(
                            By.XPATH, 
                            ".//button[contains(@aria-label, 'Comment') or contains(@data-control-name, 'comment')]"
                        )
                        if comment_button:
                            comment_button.click()
                            print("💬 Comment button clicked.")
                            break
                    except Exception:
                        print(f"[⚠️] Attempt {attempt + 1} failed to find the comment button.")
                        time.sleep(1)
                
                if not comment_button:
                    print("[❌] Could not find the comment button after multiple attempts.")
                    return  # Exit early if the comment button is not found

                # Wait for the rich text editor (comment box) to appear
                for attempt in range(retries):
                    try:
                        # Locate the contenteditable div inside the rich text editor
                        comment_box = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"))
                        )
                        
                        # Debug: Print the HTML of the located element
                        print(f"[🔍] Found comment box: {comment_box.get_attribute('outerHTML')}")

                        # Allow user to input their own comment
                        custom_comment = input("📝 Enter your comment: ").strip()
                        if not custom_comment:
                            custom_comment = "Thanks for sharing! 👏"  # Default fallback

                        # Use JavaScript to set the value of the contenteditable div
                        driver.execute_script("arguments[0].innerHTML = arguments[1];", comment_box, custom_comment)
                        print("💬 Comment written.")
                        
                        # Locate and click the "Comment" submit button
                        submit_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'comments-comment-box__submit-button')]"))
                        )
                        submit_button.click()
                        print("💬 Comment submitted.")
                        break  # Exit retry loop if successful
                    except Exception as e:
                        print(f"[⚠️] Attempt {attempt + 1} failed to interact with the comment box: {e}")
                        if attempt == retries - 1:
                            print("[❌] Failed to comment after multiple attempts.")
            except Exception as e:
                print(f"[⚠️] Couldn't find or click the comment button: {e}")
        
        else:
            print("⏭️ Skipped.")
    
    except Exception as e:
        print(f"[⚠️] Failed on post #{index + 1}: {e}")

def engage_feed(driver, max_posts=5): 
    print("📜 Scrolling to load posts...") 
    scroll_slowly(driver, max_scrolls=6)
    
    posts = get_post_containers(driver)
    print(f"🔍 Found {len(posts)} posts.")
    
    for i, post in enumerate(posts[:max_posts]):
        process_post(driver, post, i)
