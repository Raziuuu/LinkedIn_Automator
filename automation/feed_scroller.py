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
        driver.execute_script("arguments[0].scrollIntoView(true);", post_element)
        time.sleep(2)
    
        # Try finding action buttons (like/comment)
        action_buttons = post_element.find_elements(By.XPATH, ".//button[contains(@aria-label, 'Like') or contains(@aria-label, 'Comment')]")
    
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
                comment_button = post_element.find_element(By.XPATH, ".//button[contains(@aria-label, 'Comment')]")
                comment_button.click()
                time.sleep(1)
    
                textarea = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[contains(@aria-label, 'Add a comment')]"))
                )
                textarea.send_keys("Thanks for sharing! 👏")
                textarea.send_keys(Keys.RETURN)
                print("💬 Commented.")
            except Exception as e:
                print(f"[⚠️] Couldn't comment: {e}")
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
