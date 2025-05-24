import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

# Add the parent directory to the path so we can import from ai
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai.ai_generator import suggest_hashtags, detect_topic_and_hashtags, enhance_caption

def submit_post(driver, log_callback=None):
    try:
        # Helper function for logging
        def log(message):
            # Print to console
            print(message)
            # If callback is provided, also send to GUI
            if log_callback:
                log_callback(message)
                
        # Try multiple methods to find the "Post" button
        try:
            log("Looking for Post button...")
            # Method 1: Using visible text
            post_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Post']]"))
            )
            log("Found Post button by visible text")
        except:
            try:
                # Method 2: Using class name
                post_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-actions__primary-action') and contains(@class, 'artdeco-button--primary')]"))
                )
                log("Found Post button by class name")
            except:
                try:
                    # Method 3: Using parent container
                    post_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='share-box_actions']//button[.//span[text()='Post']]"))
                    )
                    log("Found Post button by parent container")
                except:
                    # Fallback: Iterate through all buttons
                    log("Primary methods failed. Using fallback...")
                    post_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in post_buttons:
                        if "Post" in btn.text:
                            post_btn = btn
                            log("Found Post button via fallback mechanism")
                            break
                    else:
                        raise Exception("Post button not found")

        # Ensure the button is visible
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_btn)
        time.sleep(1)

        # Try different click methods
        try:
            log("Attempting JavaScript click...")
            driver.execute_script("arguments[0].click();", post_btn)
        except:
            try:
                log("Attempting ActionChains click...")
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_to_element(post_btn).click().perform()
            except:
                log("Attempting regular click...")
                post_btn.click()

        log("✅ Post submitted.")
        time.sleep(5)

        # Verify post was successful
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"))
            )
            log("✅ Post confirmed on feed.")
        except:
            log("⚠️ Post submission attempted, but couldn't verify post on feed.")

    except Exception as e:
        log(f"❌ Failed to click Post button: {e}")
        driver.save_screenshot("post_button_error.png")
        raise

def open_post_modal(driver, log_callback=None):
    try:
        # Helper function for logging
        def log(message):
            # Print to console
            print(message)
            # If callback is provided, also send to GUI
            if log_callback:
                log_callback(message)
                
        driver.get("https://www.linkedin.com/feed/")
        log("Navigating to LinkedIn feed...")
        
        # Wait longer for the feed to fully load and stabilize
        time.sleep(5)
        
        # Get screenshot for debugging
        driver.save_screenshot("before_click.png")
        
        # Try multiple methods with better targeting
        try:
            # Method 1: Target the specific button by ID
            log("Trying to locate 'Start a post' button by ID...")
            # Use the ember ID (but note that these IDs can change between sessions)
            ember_buttons = driver.find_elements(By.CSS_SELECTOR, "[id^='ember'][class*='artdeco-button']")
            
            for btn in ember_buttons:
                if "Start a post" in btn.text:
                    log(f"Found button with text: {btn.text}")
                    # Scroll to ensure it's in view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(2)
                    # Try to remove any overlays that might intercept
                    driver.execute_script("""
                        var overlays = document.querySelectorAll('[class*="overlay"], [class*="popup"], [class*="modal"]');
                        for(var i=0; i<overlays.length; i++) {
                            if(overlays[i].style.display !== 'none') {
                                overlays[i].style.display = 'none';
                            }
                        }
                    """)
                    time.sleep(1)
                    # Click using JavaScript
                    driver.execute_script("arguments[0].click();", btn)
                    break
            else:
                raise Exception("Button with 'Start a post' text not found")
                
        except Exception as e:
            log(f"ID method failed: {e}")
            try:
                # Method 2: Try direct XPath with contains for the specific class you shared
                log("Trying specific class selector...")
                post_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".iJgxIKBnhIZuvAnUHEGlRLCUgQuzvthjEUODyac"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_button)
                time.sleep(1)
                # Click using Actions
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_to_element(post_button).click().perform()
                
            except Exception as e2:
                log(f"Class selector method failed: {e2}")
                # Method 3: Try clicking any element that has "Start a post" text
                log("Trying text search...")
                try:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Start a post')]")
                    if elements:
                        for elem in elements:
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", elem)
                                break
                            except:
                                continue
                    else:
                        raise Exception("No elements with 'Start a post' text found")
                except Exception as e3:
                    log(f"Text search failed: {e3}")
                    raise Exception("Could not open post modal with any method")

        # Verify the post modal is open
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@role, 'textbox')]"))
        )
        log("📝 Opened post modal.")
        return True
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to open post modal: {e}")
        print(f"❌ Failed to open post modal: {e}")
        driver.save_screenshot("debug_post_modal_failure.png")  # Save a screenshot for debugging
        return False

def upload_image(driver, image_path, log_callback=None):
    try:
        # Helper function for logging
        def log(message):
            # Print to console
            print(message)
            # If callback is provided, also send to GUI
            if log_callback:
                log_callback(message)
                
        log("Attempting to upload image...")
        
        # Try multiple selectors to find the image upload button
        selectors = [
            # First option: from feed view
            "//button[contains(@class, 'image_video-detour-btn') or contains(@aria-label, 'Add media')]",
            # Second option: from post creation window
            "//span[contains(@class, 'share-promoted-detour-button__icon-container')]",
            # Additional selectors for other possible UI variations
            "//button[contains(@aria-label, 'Add a photo')]",
            "//button[.//span[text()='Media']]",
            "//button[contains(@class, 'artdeco-button')][.//span[text()='Media']]",
            # Try by icon
            "//*[name()='svg'][@data-test-icon='image-medium']/parent::*",
            # Generic option
            "//*[contains(text(), 'Add media') or contains(text(), 'Media') or contains(text(), 'Add a photo')]"
        ]
        
        # Try each selector
        for selector in selectors:
            try:
                log(f"Trying selector: {selector}")
                image_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # Scroll to ensure button is visible
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", image_button)
                time.sleep(1)
                
                # Try JavaScript click first (less likely to be intercepted)
                try:
                    driver.execute_script("arguments[0].click();", image_button)
                except:
                    # If JS click fails, try regular click
                    image_button.click()
                
                log("✅ Clicked media upload button")
                break
            except Exception as e:
                log(f"Selector failed: {str(e)[:100]}...")
                continue
        else:
            # If all selectors fail, try a final JavaScript approach
            log("All selectors failed, using JavaScript traversal...")
            driver.execute_script("""
                // Look for buttons with media-related text or icons
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    if (btn.textContent.includes('Media') || 
                        btn.getAttribute('aria-label')?.includes('media') || 
                        btn.getAttribute('aria-label')?.includes('photo') ||
                        btn.innerHTML.includes('image-medium')) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            """)
        
        # Wait for file input to appear
        time.sleep(2)
        
        # Try multiple ways to find the file input
        try:
            log("Looking for file input...")
            
            # Try standard method first
            file_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            
            # Ensure the path is absolute
            abs_path = os.path.abspath(image_path)
            log(f"Uploading file: {abs_path}")
            
            # Upload the file
            file_input.send_keys(abs_path)
            
            log("🖼️ Image selected.")
            time.sleep(3)
            
            # Check if there's a "Done" button and click it
            try:
                done_selectors = [
                    "//button[contains(@aria-label, 'Done')]",
                    "//button[text()='Done']",
                    "//div[contains(@class, 'share-box-footer')]//button[contains(@class, 'primary')]"
                ]
                
                for done_selector in done_selectors:
                    try:
                        done_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, done_selector))
                        )
                        done_button.click()
                        log("✅ Clicked Done button")
                        break
                    except:
                        continue
            except:
                log("No Done button found or not needed")
                
            log("✅ Image uploaded.")
            return True
            
        except Exception as e:
            log(f"❌ Failed to upload file: {str(e)}")
            return False
            
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to upload image: {e}")
        print(f"❌ Failed to upload image: {e}")
        driver.save_screenshot("image_upload_error.png")
        return False
    
def schedule_post(driver):
    try:
        print("📆 Opening scheduling modal...")

        # Click the scheduling (clock) icon next to Post button
        schedule_selectors = [
            "//button[contains(@aria-label, 'Schedule')]",
            "//button[contains(@class, 'schedule-button')]",
            "//button[.//span[contains(text(), 'Schedule')]]",
            "//div[contains(@class, 'share-box-footer')]//button[contains(@class, 'schedule')]"
        ]
        
        for selector in schedule_selectors:
            try:
                clock_icon = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clock_icon)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", clock_icon)
                print(f"Clicked schedule button using selector: {selector}")
                break
            except:
                continue
        else:
            # If none of the above selectors work, try a JavaScript approach
            print("Using JavaScript to find and click schedule button...")
            driver.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.includes('Schedule') || 
                        buttons[i].getAttribute('aria-label')?.includes('Schedule')) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """)
        
        time.sleep(2)

        # Wait for scheduling modal to appear
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "share-post__scheduled-date"))
        )
        
        # Get current time and calculate minimum valid time (current + 10 minutes)
        from datetime import datetime, timedelta
        current_time = datetime.now()
        min_valid_time = current_time + timedelta(minutes=15)  # Adding 15 min for safety
        
        # Format as string to show user
        min_time_str = min_valid_time.strftime("%m/%d/%Y %I:%M %p")
        print(f"NOTE: Schedule time must be at least 10 minutes in the future (after {min_time_str})")
        
        # Ask for date and time with validation
        while True:
            date_str = input("Enter the date (mm/dd/yyyy): ")
            time_str = input("Enter the time (e.g., 10:00 AM): ")
            
            # Attempt to parse the user's input
            try:
                # Try different time formats
                try:
                    user_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p")
                except:
                    try:
                        user_datetime = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
                    except:
                        print("❌ Invalid date/time format. Please try again.")
                        continue
                
                # Check if time is at least 10 minutes in the future
                if user_datetime <= min_valid_time:
                    print(f"❌ Schedule time must be after {min_time_str}. Please try again.")
                    continue
                
                # Valid time, exit loop
                break
            except Exception as e:
                print(f"❌ Invalid date/time format: {e}. Please try again.")
        
        # Input date field
        date_input = driver.find_element(By.ID, "share-post__scheduled-date")
        date_input.clear()
        date_input.send_keys(date_str)
        print(f"Date set to: {date_str}")
        time.sleep(1)

        # Input time field
        time_input = driver.find_element(By.ID, "share-post__scheduled-time")
        time_input.clear()
        time_input.send_keys(time_str)
        print(f"Time set to: {time_str}")
        time.sleep(1)

        # Updated Code
        next_button_selectors = [
            "//button[@aria-label='Next']",  # Using aria-label
            "//button[contains(@class, 'artdeco-button--primary') and .//span[text()='Next']]",  # Using class and text
            "//span[text()='Next']/ancestor::button",  # Using the span text and ancestor button
        ]

        for selector in next_button_selectors:
            try:
                next_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"Found 'Next' button using selector: {selector}")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                print("Clicked 'Next' button using JavaScript")
                break
            except Exception as e:
                print(f"Failed with selector {selector}: {str(e)[:50]}...")
        else:
            raise Exception("Could not find or click the 'Next' button.")
        
        time.sleep(2)
        
        # Wait for and click the final "Schedule" button that appears after clicking Next
        # Using multiple selectors to find the final Schedule button
        schedule_confirmation_selectors = [
            "//button[.//span[text()='Schedule']]",
            "//button[contains(@class, 'share-actions__primary-action')]",
            "//button[@id='ember415']",  # ID from your example, but IDs might change
            "//button[contains(@class, 'artdeco-button--primary')][.//span[text()='Schedule']]"
        ]
        
        for selector in schedule_confirmation_selectors:
            try:
                schedule_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"Found final Schedule button with selector: {selector}")
                # Scroll to ensure it's visible
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", schedule_btn)
                time.sleep(1)
                # Click using JavaScript
                driver.execute_script("arguments[0].click();", schedule_btn)
                break
            except Exception as e:
                print(f"Failed with selector {selector}: {str(e)[:50]}...")
                continue
        else:
            # If all selectors fail, try a final JavaScript approach
            print("Using JavaScript to find and click final Schedule button...")
            driver.execute_script("""
                var buttons = document.querySelectorAll('button');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.trim() === 'Schedule') {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """)
        
        # Wait for confirmation that the post was scheduled
        time.sleep(3)
        driver.save_screenshot("schedule_confirmation.png")
        
        print(f"✅ Post scheduled for {date_str} at {time_str}")
        return True
        
    except Exception as e:
        print(f"❌ Scheduling failed: {e}")
        driver.save_screenshot("schedule_error.png")
        return False


def create_post_alternative_route(driver, caption, image_path=None, smart=False, log_callback=None):
    """Alternative method to create post when the modal approach fails"""
    try:
        # Helper function for logging
        def log(message):
            # Print to console
            print(message)
            # If callback is provided, also send to GUI
            if log_callback:
                log_callback(message)
        
        # Go directly to the post creation page
        driver.get("https://www.linkedin.com/post/new/")
        time.sleep(5)

        # Fill in the caption
        try:
            text_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@role, 'textbox')]"))
            )
            if smart:
                try:
                    topic, hashtags = detect_topic_and_hashtags(caption)
                    print(f"🧠 Detected Topic: {topic}")
                    print(f"#️⃣ Suggested Hashtags: {' '.join(hashtags)}")
                    
                    user_choice = input("Use suggested hashtags? [y = yes / e = edit / n = none]: ").strip().lower()
                    if user_choice == 'e':
                        custom = input("Enter your own hashtags (space-separated): ").strip()
                        hashtags = custom.split()
                    elif user_choice == 'n':
                        hashtags = []
                except Exception as e:
                    print(f"⚠️ Smart hashtag detection failed: {e}")
                    print("Continuing without hashtags.")
                    hashtags = []
            else:
                try:
                    hashtags = suggest_hashtags(caption)
                except Exception as e:
                    print(f"⚠️ Hashtag suggestion failed: {e}")
                    print("Continuing without hashtags.")
                    hashtags = []

            # Add hashtags if any were generated or provided
            if hashtags:
                full_caption = f"{caption}\n{' '.join(hashtags)}"
            else:
                full_caption = caption
                
            text_area.send_keys(full_caption)
            log(f"📝 Post caption filled:\n{full_caption}")
            time.sleep(2)
        except Exception as e:
            log(f"❌ Failed to fill post caption: {e}")
            return False

        # Add image if provided
        if image_path:
            try:
                # Look for media upload button
                media_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Add media') or contains(@aria-label, 'photo') or contains(@aria-label, 'image')]")
                if media_buttons:
                    media_buttons[0].click()
                    time.sleep(2)
                    # Locate the file input field and upload the image
                    file_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    file_input.send_keys(os.path.abspath(image_path))
                    log("🖼️ Image selected.")
                    time.sleep(3)
                    # Look for a Done button
                    done_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Done') or contains(text(), 'Done')]")
                    if done_buttons:
                        done_buttons[0].click()
                        log("✅ Image uploaded.")
                        time.sleep(2)
            except Exception as e:
                log(f"❌ Failed to upload image: {e}")

        # Ask user before posting
        confirm = input("🚀 Ready to post? [y/n]: ").strip().lower()
        if confirm != 'y':
            log("❌ Post canceled.")
            return False

        # Submit the post using the new `submit_post` function
        try:
            submit_post(driver, log_callback)
            log("✅ Post submitted")
            return True
        except Exception as e:
            log(f"❌ Post submission failed: {e}")
            return False
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Alternative posting method failed: {e}")
        print(f"❌ Alternative posting method failed: {e}")
        driver.save_screenshot("alternative_post_failure.png")
        return False

def create_linkedin_post(driver, caption, image_path=None, smart=False, log_callback=None):
    try:
        # Helper function for logging
        def log(message):
            # Print to console
            print(message)
            # If callback is provided, also send to GUI
            if log_callback:
                log_callback(message)
        
        # Clean the caption first
        def remove_non_bmp(text):
            return ''.join(char for char in text if ord(char) < 0x10000)
        
        clean_caption = remove_non_bmp(caption)
        
        # Try the standard posting method first
        if open_post_modal(driver, log_callback):
            try:
                # Wait for the post text area
                post_text_area = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@role, 'textbox')]"))
                )
                
                # Clear any existing text and enter the caption
                post_text_area.clear()
                post_text_area.send_keys(clean_caption)
                log("✅ Caption entered successfully")
                
                # Handle image upload if provided
                if image_path:
                    if upload_image(driver, image_path, log_callback):
                        log("✅ Image uploaded successfully")
                    else:
                        log("⚠️ Image upload failed")
                
                # Handle smart hashtags if enabled
                if smart:
                    try:
                        topic, hashtags = detect_topic_and_hashtags(clean_caption)
                        if hashtags:
                            post_text_area.send_keys("\n\n" + " ".join(hashtags))
                            log("✅ Smart hashtags added")
                    except Exception as e:
                        log(f"⚠️ Smart hashtag detection failed: {e}")
                        log("Continuing without hashtags.")
                
                # Submit the post
                submit_post(driver, log_callback)
                log("✅ Post submitted")
                return True
                
            except Exception as e:
                log(f"❌ Failed to fill post caption: {e}")
                return False
        else:
            log("⚠️ Standard posting method failed. Trying alternative route...")
            return create_post_alternative_route(driver, clean_caption, image_path, smart, log_callback)
            
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Post creation failed: {e}")
        print(f"❌ Post creation failed: {e}")
        return False

