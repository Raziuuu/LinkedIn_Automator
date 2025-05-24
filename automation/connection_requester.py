import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_people_you_may_know(driver, output_callback=None):
    """Open the LinkedIn 'My Network' page."""
    if output_callback:
        output_callback("🔄 Opening LinkedIn network page...\n", level="info")
    driver.get("https://www.linkedin.com/mynetwork/")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        time.sleep(3)
        if output_callback:
            output_callback("✅ Network page loaded\n", level="user")
    except TimeoutException:
        if output_callback:
            output_callback("⚠️ Page load timeout, continuing...\n", level="info")

def get_connection_sections(driver, output_callback=None):
    """Get all connection sections (profile cards)."""
    sections = {}
    try:
        # Updated selectors to target profile cards more reliably
        section_selectors = [
            "//div[contains(@class, 'discover-person-card') or contains(@class, 'mn-connection-card') or @data-view-name='profile-card']",
            "//div[.//button[contains(@aria-label, 'Invite') or contains(text(), 'Connect')]]",
            "//div[contains(@class, 'artdeco-card') and .//span[contains(@class, 'discover-person-card__name')]]"
        ]
        
        headers = []
        for selector in section_selectors:
            try:
                # Wait for at least one profile card to be visible
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                headers = driver.find_elements(By.XPATH, selector)
                if headers and output_callback:
                    output_callback(f"📋 Found {len(headers)} profile cards\n", level="info")
                break
            except TimeoutException:
                if output_callback:
                    output_callback(f"⚠️ No profile cards found with selector: {selector}\n", level="debug")
                continue
        
        if not headers and output_callback:
            output_callback("⚠️ No profile cards found across all selectors\n", level="user")
            return sections
        
        for header in headers:
            try:
                # Extract a unique identifier for the card (e.g., name or title)
                name_element = header.find_element(By.XPATH, ".//span[contains(@class, 'discover-person-card__name') or contains(@aria-label, 'View')]")
                section_title = name_element.text.strip()[:50] + "..." if len(name_element.text.strip()) > 50 else name_element.text.strip()
                if not section_title or "Manage" in section_title or "Training" in section_title or "invited" in section_title:
                    continue
                sections[section_title] = header
            except Exception as e:
                if output_callback:
                    output_callback(f"⚠️ Error processing card: {str(e)}\n", level="debug")
                
    except Exception as e:
        if output_callback:
            output_callback(f"❌ Error finding cards: {str(e)}\n", level="debug")
        
    return sections

def extract_profile_cards(section_element, driver, output_callback=None):
    """Treat section element as a profile card."""
    try:
        if section_element:
            connect_button = get_connect_button(section_element)
            if connect_button:
                if output_callback:
                    output_callback("🔍 Found 1 profile card\n", level="info")
                return [section_element]
            else:
                if output_callback:
                    output_callback("⚠️ No connect button found for card\n", level="info")
                return []
    except Exception as e:
        if output_callback:
            output_callback(f"❌ Error extracting card: {str(e)}\n", level="debug")
    return []

def extract_profile_info(card):
    """Extract profile information from a card."""
    try:
        name = headline = location = university = company = "N/A"
        
        name_selectors = [
            ".//span[contains(@class, 'discover-person-card__name')]",
            ".//p[contains(@class, '_08b3c87c') and contains(@class, '_60273cc6')]",
            ".//span[contains(@aria-label, 'View') and contains(@aria-label, 'profile')]"
        ]
        
        for selector in name_selectors:
            try:
                name_element = card.find_element(By.XPATH, selector)
                name = name_element.text.strip()
                if name and name != "N/A":
                    break
            except:
                continue
        
        headline_selectors = [
            ".//p[contains(@class, 'discover-person-card__occupation')]",
            ".//p[contains(@class, '_08b3c87c') and contains(@class, '_474cacb5')]",
            ".//div[contains(@class, 'artdeco-entity-lockup__content')]//p[2]"
        ]
        
        for selector in headline_selectors:
            try:
                headline_element = card.find_element(By.XPATH, selector)
                headline = headline_element.text.strip()
                if headline:
                    break
            except:
                continue
        
        try:
            location_element = card.find_element(
                By.XPATH, ".//*[contains(text(), ', ') and not(contains(text(), 'Works at')) and not(contains(text(), 'Attended'))]"
            )
            location_text = location_element.text.strip()
            if ", " in location_text:
                location = location_text.split(", ")[-1].strip()
        except:
            pass
        
        try:
            university_element = card.find_element(
                By.XPATH, ".//*[contains(text(), 'Attended') or contains(text(), 'Studied at') or contains(text(), 'University') or contains(text(), 'College')]"
            )
            university_text = university_element.text
            if "Attended " in university_text:
                university = university_text.split("Attended ")[-1].strip()
            elif "Studied at " in university_text:
                university = university_text.split("Studied at ")[-1].strip()
            else:
                university = university_text.strip()
        except:
            pass
        
        try:
            company_element = card.find_element(
                By.XPATH, ".//*[contains(text(), 'Works at') or contains(text(), ' at ')]"
            )
            company_text = company_element.text
            if "Works at " in company_text:
                company = company_text.split("Works at ")[-1].strip()
            elif " at " in company_text and "Attended" not in company_text:
                company = company_text.split(" at ")[-1].strip()
            else:
                company = company_text.strip()
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
        return {
            "name": "Unknown",
            "headline": "N/A", 
            "location": "N/A",
            "connections": "N/A",
            "university": "N/A",
            "company": "N/A",
        }

def get_connect_button(card):
    """Find the connect button in a profile card."""
    connect_selectors = [
        ".//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]",
        ".//button[@data-view-name='edge-creation-connect-action']",
        ".//button[contains(text(), 'Connect') and contains(@class, 'artdeco-button')]"
    ]
    
    retries = 2
    while retries > 0:
        for selector in connect_selectors:
            try:
                button = card.find_element(By.XPATH, selector)
                return button
            except NoSuchElementException:
                continue
        retries -= 1
        time.sleep(1)
    return None

def send_connection_request(driver, card, button, message, output_callback=None):
    """Send a connection request."""
    try:
        driver.execute_script(
            "arguments[0].style.border='2px solid green'; arguments[0].style.backgroundColor='#f0fff0';", card
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(1)
        
        ActionChains(driver).move_to_element(button).click().perform()
        time.sleep(5)
        
        success = False
        try:
            send_buttons = [
                "//button[contains(text(), 'Send invitation')]",
                "//button[contains(text(), 'Send now')]", 
                "//button[@aria-label='Send invitation']",
                "//button[@aria-label='Send now']"
            ]
            for btn_selector in send_buttons:
                try:
                    send_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, btn_selector))
                    )
                    send_btn.click()
                    time.sleep(2)
                    success = True
                    if output_callback:
                        output_callback("✅ Connection request sent via modal\n", level="user")
                    break
                except TimeoutException:
                    continue
        except:
            pass
        
        if not success:
            try:
                status_selectors = [
                    "//button[contains(@aria-label, 'Pending')]",
                    "//button[contains(@aria-label, 'Sent')]",
                    "//button[contains(text(), 'Pending')]"
                ]
                for status_selector in status_selectors:
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, status_selector))
                        )
                        success = True
                        if output_callback:
                            output_callback("✅ Connection request sent successfully\n", level="user")
                        break
                    except TimeoutException:
                        continue
            except:
                pass
        
        if not success:
            success = True
            if output_callback:
                output_callback("✅ Connection request likely sent\n", level="user")
            
        if success:
            driver.execute_script(
                "arguments[0].style.border='2px solid blue'; arguments[0].style.backgroundColor='#e6f7ff';", card
            )
        return success
            
    except ElementClickInterceptedException:
        if output_callback:
            output_callback("❌ Could not click connect button\n", level="user")
        driver.execute_script(
            "arguments[0].style.border='2px solid red'; arguments[0].style.backgroundColor='#fff1f0';", card
        )
        return False
    except Exception as e:
        if output_callback:
            output_callback(f"❌ Error sending connection: {str(e)}\n", level="user")
        return False

def scroll_to_load_more(driver, times=10, output_callback=None):
    """Scroll the page to load more connections."""
    if output_callback:
        output_callback("📜 Scrolling to load more profiles...\n", level="info")
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(4, 6))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            if output_callback:
                output_callback("✅ No more profiles to load\n", level="info")
            break
        last_height = new_height
    # Wait for profiles to be visible after scrolling
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'discover-person-card') or contains(@class, 'mn-connection-card') or @data-view-name='profile-card']"
            ))
        )
        if output_callback:
            output_callback("✅ Profiles loaded after scrolling\n", level="info")
    except TimeoutException:
        if output_callback:
            output_callback("⚠️ No profiles visible after scrolling\n", level="info")
    if output_callback:
        output_callback("✅ Done scrolling\n", level="info")

processed_profiles = set()
skipped_profiles = set()
saved_for_later = set()

def print_profile_info(profile_info, output_callback=None):
    """Display profile information."""
    output = "\n" + "=" * 50 + "\n"
    output += f"👤 {profile_info['name']}\n"
    output += f"💼 {profile_info['headline']}\n"
    if profile_info['location'] != "N/A":
        output += f"📍 {profile_info['location']}\n"
    if profile_info['university'] != "N/A":
        output += f"🎓 {profile_info['university']}\n"
    if profile_info['company'] != "N/A":
        output += f"🏢 {profile_info['company']}\n"
    output += "=" * 50 + "\n"
    if output_callback:
        output_callback(output, level="user")

def process_connections(driver, max_requests=5, output_callback=None, decision_callback=None, counter_callback=None):
    """Process connection requests."""
    global processed_profiles, skipped_profiles, saved_for_later
    
    open_people_you_may_know(driver, output_callback)
    scroll_to_load_more(driver, output_callback=output_callback)

    sections = get_connection_sections(driver, output_callback)
    if not sections:
        if output_callback:
            output_callback("❌ No profiles found. Trying direct profile search...\n", level="user")
        process_all_profiles(driver, max_requests, output_callback, decision_callback, counter_callback)
        return

    total_requests_sent = 0
    processed_in_this_run = set()

    for section_title, section_element in sections.items():
        if total_requests_sent >= max_requests:
            break

        if output_callback:
            output_callback(f"\n🔶 Processing profile: {section_title[:30]}...\n", level="user")

        cards = extract_profile_cards(section_element, driver, output_callback)
        if not cards:
            continue

        for card in cards:
            if total_requests_sent >= max_requests:
                break

            retries = 2
            while retries > 0:
                try:
                    profile_info = extract_profile_info(card)
                    name = profile_info['name']

                    if name == "N/A" or name == "Unknown" or not name.strip():
                        if output_callback:
                            output_callback(f"⚠️ Skipping invalid profile: {name}\n", level="user")
                        break
                
                    if name in processed_in_this_run or name in processed_profiles:
                        if output_callback:
                            output_callback(f"⚠️ Skipping already processed: {name}\n", level="user")
                        break

                    processed_in_this_run.add(name)
                    driver.execute_script(
                        "arguments[0].style.border='2px solid green';", card
                    )
                    print_profile_info(profile_info, output_callback)

                    while True:
                        if output_callback:
                            output_callback("🤖 Send request? [y/n/l]: ", level="user")
                        decision = decision_callback()
                        if decision == "y":
                            connect_button = get_connect_button(card)
                            if connect_button:
                                success = send_connection_request(driver, card, connect_button, None, output_callback)
                                if success:
                                    total_requests_sent += 1
                                    processed_profiles.add(name)
                                    if output_callback:
                                        output_callback(f"📊 Progress: {total_requests_sent}/{max_requests} requests sent\n", level="user")
                                    if counter_callback:
                                        global connections_sent
                                        connections_sent = total_requests_sent
                                        counter_callback()
                            else:
                                if output_callback:
                                    output_callback("❌ No connect button found\n", level="user")
                            break
                        elif decision == "n":
                            skipped_profiles.add(name)
                            if output_callback:
                                output_callback("⏭️ Skipped\n", level="user")
                            driver.execute_script(
                                "arguments[0].style.border='2px solid gray';", card
                            )
                            if counter_callback:
                                global connections_skipped
                                connections_skipped += 1
                                counter_callback()
                            break
                        elif decision == "l":
                            saved_for_later.add(name)
                            if output_callback:
                                output_callback("📌 Saved for later\n", level="user")
                            if counter_callback:
                                global connections_saved
                                connections_saved += 1
                                counter_callback()
                            break
                        else:
                            if output_callback:
                                output_callback("⚠️ Invalid option. Choose [y/n/l]\n", level="user")

                    time.sleep(random.uniform(1, 2))
                    break

                except StaleElementReferenceException:
                    if output_callback:
                        output_callback("⚠️ Stale element, retrying...\n", level="info")
                    retries -= 1
                    time.sleep(1)
                    continue
                except Exception as e:
                    if output_callback:
                        output_callback(f"❌ Error processing profile: {str(e)}\n", level="user")
                    break
            if retries == 0:
                if output_callback:
                    output_callback("❌ Failed to process profile after retries\n", level="user")
                continue

def process_all_profiles(driver, max_requests, output_callback, decision_callback, counter_callback):
    """Process all profiles on the page without relying on sections."""
    global processed_profiles, connections_sent, connections_skipped, connections_saved
    total_requests_sent = 0
    processed_in_this_run = set()
    
    try:
        card_selectors = [
            "//div[contains(@class, 'discover-person-card') or contains(@class, 'mn-connection-card') or @data-view-name='profile-card']",
            "//div[.//button[contains(@aria-label, 'Invite') or contains(text(), 'Connect')]]",
            "//div[contains(@class, 'artdeco-card') and .//span[contains(@class, 'discover-person-card__name')]]"
        ]
        
        cards = []
        for selector in card_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                cards = driver.find_elements(By.XPATH, selector)
                if cards and output_callback:
                    output_callback(f"🔍 Found {len(cards)} profiles\n", level="info")
                break
            except TimeoutException:
                if output_callback:
                    output_callback(f"⚠️ No profiles found with selector: {selector}\n", level="debug")
                continue
        
        if not cards and output_callback:
            output_callback("❌ No profiles found across all selectors\n", level="user")
            return
        
        for card in cards:
            if total_requests_sent >= max_requests:
                break
                
            retries = 2
            while retries > 0:
                try:
                    profile_info = extract_profile_info(card)
                    name = profile_info['name']

                    if name == "N/A" or name == "Unknown" or not name.strip():
                        if output_callback:
                            output_callback(f"⚠️ Skipping invalid profile: {name}\n", level="user")
                        break
                
                    if name in processed_in_this_run or name in processed_profiles:
                        if output_callback:
                            output_callback(f"⚠️ Skipping already processed: {name}\n", level="user")
                        break

                    processed_in_this_run.add(name)
                    driver.execute_script(
                        "arguments[0].style.border='2px solid green';", card
                    )
                    print_profile_info(profile_info, output_callback)

                    while True:
                        if output_callback:
                            output_callback("🤖 Send request? [y/n/l]: ", level="user")
                        decision = decision_callback()
                        if decision == "y":
                            connect_button = get_connect_button(card)
                            if connect_button:
                                success = send_connection_request(driver, card, connect_button, None, output_callback)
                                if success:
                                    total_requests_sent += 1
                                    processed_profiles.add(name)
                                    if output_callback:
                                        output_callback(f"📊 Progress: {total_requests_sent}/{max_requests} requests sent\n", level="user")
                                    if counter_callback:
                                        connections_sent = total_requests_sent
                                        counter_callback()
                            else:
                                if output_callback:
                                    output_callback("❌ No connect button found\n", level="user")
                            break
                        elif decision == "n":
                            skipped_profiles.add(name)
                            if output_callback:
                                output_callback("⏭️ Skipped\n", level="user")
                            driver.execute_script(
                                "arguments[0].style.border='2px solid gray';", card
                            )
                            if counter_callback:
                                connections_skipped += 1
                                counter_callback()
                            break
                        elif decision == "l":
                            saved_for_later.add(name)
                            if output_callback:
                                output_callback("📌 Saved for later\n", level="user")
                            if counter_callback:
                                connections_saved += 1
                                counter_callback()
                            break
                        else:
                            if output_callback:
                                output_callback("⚠️ Invalid option. Choose [y/n/l]\n", level="user")

                    time.sleep(random.uniform(1, 2))
                    break
                    
                except StaleElementReferenceException:
                    if output_callback:
                        output_callback("⚠️ Stale element, retrying...\n", level="info")
                    retries -= 1
                    time.sleep(1)
                    continue
                except Exception as e:
                    if output_callback:
                        output_callback(f"❌ Error processing profile: {str(e)}\n", level="user")
                    break
            if retries == 0:
                if output_callback:
                    output_callback("❌ Failed to process profile after retries\n", level="user")
                continue
                
    except Exception as e:
        if output_callback:
            output_callback(f"❌ Error finding profiles: {str(e)}\n", level="user")