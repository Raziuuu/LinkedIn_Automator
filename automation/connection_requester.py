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

# Global sets for tracking processed profiles
processed_profiles = set()
skipped_profiles = set()
saved_for_later = set()

def reset_counters():
    """Reset global tracking sets."""
    global processed_profiles, skipped_profiles, saved_for_later
    processed_profiles = set()
    skipped_profiles = set()
    saved_for_later = set()

def open_people_you_may_know(driver, output_callback=None):
    """Open the LinkedIn 'My Network' page."""
    if output_callback:
        output_callback("🔄 Opening LinkedIn network page...", level="info")
    driver.get("https://www.linkedin.com/mynetwork/")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        time.sleep(3)
        if output_callback:
            output_callback("✅ Network page loaded", level="user")
    except TimeoutException:
        if output_callback:
            output_callback("⚠ Page load timeout, continuing...", level="info")

def scroll_to_load_more(driver, output_callback=None):
    """Scroll the page to load more profiles."""
    if output_callback:
        output_callback("📜 Scrolling to load more profiles...", level="info")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            if output_callback:
                output_callback("✅ No more profiles to load", level="info")
            break
        last_height = new_height
    if output_callback:
        output_callback("✅ Done scrolling", level="info")

def get_connection_sections(driver, output_callback=None):
    """Get all connection sections (profile cards)."""
    sections = {}
    
    # Primary selector from the simplified version
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "discover-entity-card"))
        )
        cards = driver.find_elements(By.CLASS_NAME, "discover-entity-card")
        if output_callback:
            output_callback(f"📋 Found {len(cards)} profile cards with class 'discover-entity-card'", level="info")
    except TimeoutException:
        if output_callback:
            output_callback("⚠ No profile cards found with class 'discover-entity-card', trying fallback selectors...", level="info")
        cards = []
    
    # Fallback selectors from the detailed version
    if not cards:
        fallback_selectors = [
            "//div[@data-view-name='cohort-card']",
            "//div[.//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]]",
            "//div[contains(@class, 'artdeco-card') and .//a[contains(@href, '/in/')]]",
        ]
        for selector in fallback_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.XPATH, selector))
                )
                cards.extend(driver.find_elements(By.XPATH, selector))
                if output_callback:
                    output_callback(f"📋 Found {len(cards)} profile cards with selector: {selector}", level="info")
            except TimeoutException:
                if output_callback:
                    output_callback(f"⚠ No profile cards found with selector: {selector}", level="debug")
    
    if not cards and output_callback:
        output_callback("⚠ No profile cards found across all selectors", level="user")
        return sections
    
    for card in cards:
        try:
            # Extract name using simplified selector, fall back to detailed selectors
            try:
                name_element = card.find_element(By.CLASS_NAME, "discover-entity-card__name")
                name = name_element.text.strip()
            except NoSuchElementException:
                name_selectors = [
                    ".//p[contains(@class, 'ac02ae51 ddce6825')]",
                    ".//p[contains(@class, 'ac02ae51') and contains(@class, '_7d7ce955')]",
                    ".//span[@dir='ltr']",
                ]
                name = "Unknown"
                for selector in name_selectors:
                    try:
                        name_element = card.find_element(By.XPATH, selector)
                        name = name_element.text.strip()
                        if name and name != "N/A":
                            break
                    except:
                        continue
            
            # Skip invalid or irrelevant profiles
            if not name or name == "Unknown" or any(x in name.lower() for x in ["manage", "training", "invited"]):
                continue
            
            profile_link = card.find_element(By.TAG_NAME, "a").get_attribute("href").split("?")[0]
            if get_connect_button(card):  # Only include cards with a connect button
                sections[name] = {
                    "element": card,
                    "profile_link": profile_link
                }
            else:
                if output_callback:
                    output_callback(f"⚠ Skipping card without connect button: {name}", level="debug")
        except Exception as e:
            if output_callback:
                output_callback(f"⚠ Error processing card: {str(e)}", level="debug")
    
    if output_callback:
        output_callback(f"📋 Total valid profile cards: {len(sections)}", level="info")
    return sections

def extract_profile_cards(section_element, driver, output_callback=None):
    """Treat section element as a profile card."""
    if get_connect_button(section_element):
        return [section_element]
    return []

def extract_profile_info(card):
    """Extract profile information from a card."""
    try:
        # Name
        try:
            name = card.find_element(By.CLASS_NAME, "discover-entity-card__name").text.strip() or "Unknown"
        except NoSuchElementException:
            name_selectors = [
                ".//p[contains(@class, 'ac02ae51 ddce6825')]",
                ".//p[contains(@class, 'ac02ae51') and contains(@class, '_7d7ce955')]",
                ".//span[@dir='ltr']",
            ]
            name = "Unknown"
            for selector in name_selectors:
                try:
                    name_element = card.find_element(By.XPATH, selector)
                    name = name_element.text.strip()
                    if name and name != "N/A":
                        break
                except:
                    continue
        
        # Headline
        try:
            headline = card.find_element(By.CLASS_NAME, "discover-entity-card__title").text.strip() or "N/A"
        except NoSuchElementException:
            headline_selectors = [
                ".//p[contains(@class, 'ac02ae51 b3a25350')]",
                ".//p[contains(@class, '_5aa7ddba')]",
                ".//div[contains(@class, 'entity-result__primary-subtitle')]",
            ]
            headline = "N/A"
            for selector in headline_selectors:
                try:
                    headline_element = card.find_element(By.XPATH, selector)
                    headline = headline_element.text.strip()
                    if headline:
                        break
                except:
                    continue
        
        # University
        university = "N/A"
        try:
            university_element = card.find_element(
                By.XPATH, ".//*[contains(text(), 'University') or contains(text(), 'College') or contains(text(), 'Studied at')]"
            )
            university_text = university_element.text.strip()
            university = university_text.split("Studied at ")[-1] if "Studied at " in university_text else university_text
        except:
            pass
        
        # Company
        company = "N/A"
        try:
            company_element = card.find_element(
                By.XPATH, ".//*[contains(text(), ' at ') and not(contains(text(), 'Studied at'))]"
            )
            company_text = company_element.text.strip()
            company = company_text.split(" at ")[-1].split(",")[0].strip()
        except:
            pass
        
        return {
            "name": name,
            "headline": headline,
            "university": university,
            "company": company,
        }
    except Exception:
        return {
            "name": "Unknown",
            "headline": "N/A",
            "university": "N/A",
            "company": "N/A",
        }

def get_connect_button(card):
    """Find the connect button in a profile card."""
    try:
        return card.find_element(By.XPATH, ".//button[contains(@aria-label, 'Invite')]")
    except NoSuchElementException:
        # Fallback selectors from the detailed version
        connect_selectors = [
            ".//button[contains(@aria-label, 'Invite') and contains(@aria-label, 'to connect')]",
            ".//button[contains(text(), 'Connect') and contains(@class, 'artdeco-button')]",
        ]
        for selector in connect_selectors:
            try:
                button = card.find_element(By.XPATH, selector)
                return button
            except NoSuchElementException:
                continue
    return None

def send_connection_request(driver, card, connect_button, message, output_callback=None):
    """Send a connection request (simplified version)."""
    try:
        driver.execute_script(
            "arguments[0].style.border='2px solid green';", card
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        time.sleep(1)
        
        ActionChains(driver).move_to_element(connect_button).click().perform()
        time.sleep(2)
        
        try:
            send_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send now']"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            if output_callback:
                output_callback("✅ Connection request sent", level="user")
            return True
        except TimeoutException:
            if output_callback:
                output_callback("✅ Connection request sent (no note)", level="user")
            return True
    except Exception as e:
        if output_callback:
            output_callback(f"❌ Failed to send request: {str(e)}", level="user")
        driver.execute_script(
            "arguments[0].style.border='2px solid red';", card
        )
        return False

def print_profile_info(profile_info, output_callback=None):
    """Display profile information."""
    output = "\n" + "=" * 50 + "\n"
    output += f"👤 {profile_info['name']}\n"
    output += f"💼 {profile_info['headline']}\n"
    if profile_info['university'] != "N/A":
        output += f"🎓 {profile_info['university']}\n"
    if profile_info['company'] != "N/A":
        output += f"🏢 {profile_info['company']}\n"
    output += f"🔗 {profile_info.get('profile_link', 'N/A')}\n"
    output += "=" * 50 + "\n"
    if output_callback:
        output_callback(output, level="user")

def process_connections(driver, max_requests=5, output_callback=None, decision_callback=None, counter_callback=None):
    """Process connection requests."""
    global processed_profiles, skipped_profiles, saved_for_later
    processed_count = 0
    
    reset_counters()
    open_people_you_may_know(driver, output_callback)
    scroll_to_load_more(driver, output_callback=output_callback)

    sections = get_connection_sections(driver, output_callback)
    if not sections:
        if output_callback:
            output_callback("❌ No profiles found to process", level="user")
        return processed_count

    total_requests_sent = 0
    processed_in_this_run = set()

    for section_title, section_data in sections.items():
        if total_requests_sent >= max_requests:
            break

        section_element = section_data["element"]
        profile_link = section_data["profile_link"]
        if output_callback:
            output_callback(f"\n🔶 Processing profile: {section_title[:30]}...", level="user")

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
                    profile_info["profile_link"] = profile_link
                    name = profile_info['name']

                    if name == "N/A" or name == "Unknown" or not name.strip():
                        if output_callback:
                            output_callback(f"⚠ Skipping invalid profile: {name}", level="user")
                        break
                
                    if name in processed_in_this_run or name in processed_profiles:
                        if output_callback:
                            output_callback(f"⚠ Skipping already processed: {name}", level="user")
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
                                    processed_count += 1
                                    processed_profiles.add(name)
                                    if output_callback:
                                        output_callback(f"📊 Progress: {total_requests_sent}/{max_requests} requests sent", level="user")
                            else:
                                if output_callback:
                                    output_callback("❌ No connect button found", level="user")
                            break
                        elif decision == "n":
                            skipped_profiles.add(name)
                            if output_callback:
                                output_callback("⏭ Skipped", level="user")
                            driver.execute_script(
                                "arguments[0].style.border='2px solid gray';", card
                            )
                            processed_count += 1
                            break
                        elif decision == "l":
                            saved_for_later.add(name)
                            if output_callback:
                                output_callback("📌 Saved for later", level="user")
                            processed_count += 1
                            break
                        else:
                            if output_callback:
                                output_callback("⚠ Invalid option. Choose [y/n/l]", level="user")

                    time.sleep(random.uniform(1, 2))
                    break

                except StaleElementReferenceException:
                    if output_callback:
                        output_callback("⚠ Stale element, retrying...", level="info")
                    retries -= 1
                    time.sleep(1)
                    continue
                except Exception as e:
                    if output_callback:
                        output_callback(f"❌ Error processing profile: {str(e)}", level="user")
                    break
            if retries == 0:
                if output_callback:
                    output_callback("❌ Failed to process profile after retries", level="user")
                continue
    
    return processed_count