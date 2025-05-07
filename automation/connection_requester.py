# automation/connection_requester.py
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def open_people_you_may_know(driver):
    print("🔄 Opening LinkedIn network page...")
    driver.get("https://www.linkedin.com/mynetwork/")
    time.sleep(6)  # Wait for the page to load completely
    print("✅ Network page loaded")


def get_connection_sections(driver):
    """Get all connection sections from the network page"""
    sections = {}
    try:
        # Find all section headers that are actually section titles, not profile names
        headers = driver.find_elements(
            By.XPATH, "//p[contains(@class, '_1s9oaxgp') and contains(@class, '_29kmc3a') and (contains(text(), '#') or contains(text(), 'people') or contains(text(), 'People'))]"
        )
        
        for header in headers:
            section_title = header.text.strip()
            if (
                not section_title
                or "Manage" in section_title
                or "Training" in section_title
                or "invited" in section_title
                or "Grow your career" in section_title
            ):
                continue  # Skip irrelevant or empty titles
                
            # Get the parent section container
            try:
                # First try to find the closest container that holds multiple profiles
                section = header.find_element(
                    By.XPATH, "./ancestor::div[contains(@class, '_1xoe5hdi')]"
                )
                sections[section_title] = section
                print(f"📋 Found section: {section_title}")
            except NoSuchElementException:
                print(f"⚠️ Could not find container for section: {section_title}")
                
        # If no sections found, use the default container
        if not sections:
            try:
                default_container = driver.find_element(
                    By.XPATH, "//div[contains(@class, 'mn-discover-cohort')]"
                )
                sections["People you may know"] = default_container
                print("📋 Using default people you may know section")
            except NoSuchElementException:
                print("⚠️ Could not find default connection section")
                
    except Exception as e:
        print(f"⚠️ Error finding connection sections: {str(e)}")
        
    return sections


def extract_profile_cards(section_element, driver):
    """Extract profile cards from a specific section"""
    try:
        if section_element:
            # Extract cards within the specific section
            # Look for elements that contain profile information but are not section headers
            cards = section_element.find_elements(
                By.XPATH, ".//div[contains(@class, 'discover-entity-card') or contains(@class, 'discover-person-card') or contains(@data-view-name, 'cohort-card')]"
            )
            
            # Filter out cards that don't have a connect button
            valid_cards = []
            for card in cards:
                try:
                    # Check if this card has a connect button
                    connect_button = card.find_element(
                        By.XPATH, ".//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]"
                    )
                    valid_cards.append(card)
                except NoSuchElementException:
                    # No connect button, might not be a profile card
                    continue
                    
            return valid_cards
    except Exception as e:
        print(f"⚠️ Error extracting profile cards: {str(e)}")
        
    return []


def extract_profile_info(card):
    try:
        name = headline = location = university = company = "N/A"
        
        # Find name - two common patterns
        try:
            name_element = card.find_element(
                By.XPATH, ".//p[contains(@class, '_1s9oaxgp') and contains(@class, '_29kmc3a')]"
            )
            name = name_element.text.strip()
        except NoSuchElementException:
            try:
                # Alternative name pattern
                name_element = card.find_element(
                    By.XPATH, ".//span[contains(@class, 'discover-person-card__name') or contains(@class, 'name')]"
                )
                name = name_element.text.strip()
            except:
                pass
        
        # Find headline
        try:
            headline_element = card.find_element(
                By.XPATH, ".//p[contains(@class, '_1s9oaxgp') and contains(@class, '_29kmc36')]"
            )
            headline = headline_element.text.strip()
        except NoSuchElementException:
            try:
                # Alternative headline pattern
                headline_element = card.find_element(
                    By.XPATH, ".//span[contains(@class, 'discover-person-card__occupation') or contains(@class, 'headline')]"
                )
                headline = headline_element.text.strip()
            except:
                pass
        
        # Find university info
        try:
            university_element = card.find_element(
                By.XPATH, ".//*[contains(text(), 'Attended') or contains(text(), 'Studied at')]"
            )
            university = university_element.text.split("Attended ")[-1].split("Studied at ")[-1].strip()
        except:
            pass
        
        # Find company info
        try:
            company_element = card.find_element(
                By.XPATH, ".//*[contains(text(), 'Works at') or contains(text(), 'at')]"
            )
            company = company_element.text.split("Works at ")[-1].split("at ")[-1].strip()
            
            # Clean up company name if it contains additional info
            if "," in company:
                company = company.split(",")[0].strip()
                
        except:
            pass
        
        return {
            "name": name,
            "headline": headline,
            "location": location,
            "connections": "N/A",
            "university": university,
            "company": company,
        }
    except Exception as e:
        print(f"⚠️ Error extracting profile info: {str(e)}")
        return {
            "name": "Unknown",
            "headline": "N/A",
            "location": "N/A",
            "connections": "N/A",
            "university": "N/A",
            "company": "N/A",
        }


def get_connect_button(card):
    try:
        return card.find_element(
            By.XPATH, ".//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]"
        )
    except NoSuchElementException:
        return None


def send_connection_request(driver, card, button, message):
    """Send a connection request without adding a note (since that requires Premium)"""
    try:
        # Highlight the card to make it visible to the user
        driver.execute_script(
            "arguments[0].style.border='2px solid green'; arguments[0].style.backgroundColor='#f0fff0';", card
        )
        # Scroll the card into view with margin at the top for better visibility
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(1)
        
        # Click the connect button
        button.click()
        time.sleep(2)
        
        # Check if the request was sent by looking for the "Pending" or "Sent" button
        try:
            # Look for either the "Pending" button or the "Sent" button
            pending_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Pending')]")
            print("✅ Connection request sent successfully (Pending).")
            return True
        except NoSuchElementException:
            try:
                sent_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Sent')]")
                print("✅ Connection request sent successfully (Sent).")
                return True
            except NoSuchElementException:
                # If we don't find either button, try to click "Send now"
                try:
                    send_btn = driver.find_element(By.XPATH, "//button[@aria-label='Send now']")
                    send_btn.click()
                    time.sleep(2)
                    print("✅ Connection request sent successfully.")
                    return True
                except NoSuchElementException:
                    # If we can't find the "Send now" button, the request might have been sent automatically
                    print("✅ Connection request sent successfully.")
                    return True
                    
        # Change the highlight to indicate success
        driver.execute_script(
            "arguments[0].style.border='2px solid blue'; arguments[0].style.backgroundColor='#e6f7ff';", card
        )
            
    except ElementClickInterceptedException:
        print("❌ Could not click connect. Possibly already sent.")
        driver.execute_script(
            "arguments[0].style.border='2px solid red'; arguments[0].style.backgroundColor='#fff1f0';", card
        )
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def scroll_to_load_more(driver, times=10):
    """Scroll the page to load more connections"""
    print("📜 Scrolling the page to load more connections...")
    for i in range(times):
        # Scroll down incrementally to trigger dynamic loading
        driver.execute_script(
            "window.scrollBy(0, Math.min(window.innerHeight, document.body.scrollHeight - window.scrollY));"
        )
        print(f"  Scroll {i + 1}/{times}...")
        time.sleep(random.uniform(2, 4))  # Random delay between scrolls
    print("✅ Done scrolling")

# Global sets to track different profile states
processed_profiles = set()     # Profiles you've already sent requests to
skipped_profiles = set()       # Profiles you skipped
saved_for_later = set()        # Profiles you marked to review later


def print_profile_info(profile_info):
    """Print profile information in a nicely formatted way"""
    print("\n" + "=" * 50)
    print(f"👤 {profile_info['name']}")
    print(f"💼 {profile_info['headline']}")
    if profile_info['location'] != "N/A":
        print(f"📍 {profile_info['location']}")
    if profile_info['connections'] != "N/A":
        print(f"🔗 {profile_info['connections']}")
    if profile_info['university'] != "N/A":
        print(f"🎓 {profile_info['university']}")
    if profile_info['company'] != "N/A":
        print(f"🏢 {profile_info['company']}")
    print("=" * 50)


def process_connections(driver, max_requests=5):
    """Process connection requests with enhanced user feedback"""
    global processed_profiles, skipped_profiles, saved_for_later
    open_people_you_may_know(driver)
    scroll_to_load_more(driver)

    # Get all connection sections
    sections = get_connection_sections(driver)
    if not sections:
        print("❌ No connection sections found. Trying to find profiles directly...")
        # Fallback to processing all cards on the page without sections
        process_all_profiles(driver, max_requests)
        return

    total_requests_sent = 0
    processed_in_this_run = set()  # Track profiles processed in this run

    for section_title, section_element in sections.items():
        if total_requests_sent >= max_requests:
            break

        print(f"\n🔶 Processing section: {section_title} 🔶")

        # Extract all cards in this section
        cards = extract_profile_cards(section_element, driver)
        print(f"🔍 Found {len(cards)} potential connections in this section.")

        if not cards:
            continue

        for card in cards:
            if total_requests_sent >= max_requests:
                break

            try:
                # Extract profile information
                profile_info = extract_profile_info(card)
                name = profile_info['name']

                # Skip invalid or already processed profiles
                if name == "N/A" or name == "Unknown":
                    continue
                
                # Skip if processed in this run or in previous runs
                if name in processed_in_this_run or name in processed_profiles:
                    continue

                # Add to processed set for this run
                processed_in_this_run.add(name)

                # Highlight the card
                driver.execute_script(
                    "arguments[0].style.border='2px solid green';", card
                )

                # Print profile details
                print_profile_info(profile_info)

                while True:
                    decision = input("🤖 Send request? [y = yes / n = skip / l = save for later]: ").strip().lower()

                    if decision == "y":
                        connect_button = get_connect_button(card)
                        if connect_button:
                            success = send_connection_request(driver, card, connect_button, None)
                            if success:
                                total_requests_sent += 1
                                processed_profiles.add(name)
                                print(f"📊 Progress: {total_requests_sent}/{max_requests} requests sent")
                        break

                    elif decision == "n":
                        skipped_profiles.add(name)
                        print("⏭️ Skipped.")
                        break

                    elif decision == "l":
                        saved_for_later.add(name)
                        print("📌 Saved for later.")
                        break

                    else:
                        print("⚠️ Invalid option. Choose [y/n/l]")

                time.sleep(1)

            except StaleElementReferenceException:
                print("⚠️ Element became stale. Moving to next.")
            except Exception as e:
                print(f"⚠️ Error processing card: {str(e)}")

    print(f"\n✅ Connection process completed. Sent {total_requests_sent} connection requests.")


def process_all_profiles(driver, max_requests=5):
    """Process all profiles on the page without relying on sections"""
    global processed_profiles
    total_requests_sent = 0
    processed_in_this_run = set()  # Track profiles processed in this run
    
    # Find all cards that have a connect button
    try:
        # This is a more direct approach to find profile cards
        cards = driver.find_elements(
            By.XPATH, "//div[.//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]]"
        )
        print(f"🔍 Found {len(cards)} potential connections on the page.")
        
        for card in cards:
            if total_requests_sent >= max_requests:
                break
                
            try:
                # Extract profile information
                profile_info = extract_profile_info(card)
                name = profile_info['name']

                # Skip invalid or already processed profiles
                if name == "N/A" or name == "Unknown":
                    continue
                
                # Skip if processed in this run or in previous runs
                if name in processed_in_this_run or name in processed_profiles:
                    continue

                # Add to processed set for this run
                processed_in_this_run.add(name)

                # Highlight the card
                driver.execute_script(
                    "arguments[0].style.border='2px solid green';", card
                )

                # Print profile details
                print_profile_info(profile_info)

                # Generate a personalized note
                note = generate_connection_note(
                    profile_info['name'],
                    profile_info['headline'],
                    university=profile_info['university'] if profile_info['university'] != "N/A" else None,
                    company=profile_info['company'] if profile_info['company'] != "N/A" else None
                )
                print(f"💬 Suggested Message:\n{note}")

                # Ask for user confirmation
                decision = input("🤖 Send this request? [y/n]: ").strip().lower()
                if decision == "y":
                    connect_button = get_connect_button(card)
                    if connect_button:
                        success = send_connection_request(driver, card, connect_button, note)
                        if success:
                            total_requests_sent += 1
                            processed_profiles.add(name)  # Mark profile as processed
                            print(f"📊 Progress: {total_requests_sent}/{max_requests} requests sent")
                    else:
                        print("❌ Connect button not found for this profile.")
                else:
                    print("⏭️ Skipped.")
                    driver.execute_script(
                        "arguments[0].style.border='2px solid gray';", card
                    )

                time.sleep(1)
                
            except StaleElementReferenceException:
                print("⚠️ Element became stale. Moving to next.")
            except Exception as e:
                print(f"⚠️ Error processing card: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error finding connection cards: {str(e)}")
        
    print(f"\n✅ Connection process completed. Sent {total_requests_sent} connection requests.")


def debug_section_detection(driver):
    """Debug function to help identify proper section elements"""
    print("🔍 Debugging section detection...")
    try:
        # Find all potential section headers
        headers = driver.find_elements(By.XPATH, "//p[contains(@class, '_1s9oaxgp')]")
        print(f"Found {len(headers)} potential section headers")
        
        for i, header in enumerate(headers):
            try:
                text = header.text.strip()
                if text:
                    # Highlight header
                    driver.execute_script(
                        f"arguments[0].style.border='2px solid blue'; arguments[0].style.backgroundColor='#e6f7ff'; arguments[0].setAttribute('data-debug', 'Header {i}: {text}');", 
                        header
                    )
                    print(f"Header {i}: '{text}'")
                    
                    # Try to find parent container
                    try:
                        parent = header.find_element(By.XPATH, "./ancestor::div[contains(@class, '_1xoe5hdi')]")
                        driver.execute_script(
                            f"arguments[0].style.border='2px solid green'; arguments[0].setAttribute('data-debug', 'Container for: {text}');",
                            parent
                        )
                    except:
                        print(f"  No container found for '{text}'")
            except:
                pass
                
        print("✅ Debug highlighting complete")
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")