from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def apply_for_jobs(driver, keywords="AI Engineer", location="India", max_applications=3):
    print(f"🔎 Navigating to LinkedIn Jobs for: {keywords} in {location}")
    
    # Navigate to jobs page and wait for initial load
    driver.get(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}")
    time.sleep(5)
    
    try:
        # Try multiple selectors for job cards
        selectors = [
            "//ul[contains(@class, 'scaffold-layout__list')]//li",
            "//div[contains(@class, 'jobs-search-results-list')]//li",
            "//div[contains(@class, 'jobs-search__results-list')]//li",
            "//div[contains(@class, 'jobs-search-results-list')]//div[contains(@class, 'job-card-container')]"
        ]
        
        job_cards = None
        for selector in selectors:
            try:
                print(f"🔍 Trying to find jobs with selector: {selector}")
                job_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, selector))
                )
                if job_cards:
                    print(f"✅ Found {len(job_cards)} job listings using selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        if not job_cards:
            print("❌ Could not find any job listings. Please check if the page loaded correctly.")
            return
        
        applied = 0
        for idx, job_card in enumerate(job_cards):
            if applied >= max_applications:
                print("✅ Reached max applications. Stopping.")
                break

            try:
                print(f"\n📄 Opening job {idx+1}")
                # Scroll the job card into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
                time.sleep(2)
                
                # Try to click the job card
                try:
                    job_card.click()
                except:
                    # If direct click fails, try JavaScript click
                    driver.execute_script("arguments[0].click();", job_card)
                
                time.sleep(3)

                # Look for the Easy Apply button with multiple possible selectors
                apply_button_selectors = [
                    "//button[contains(@class, 'jobs-apply-button')]",
                    "//button[contains(text(), 'Easy Apply')]",
                    "//button[contains(@class, 'jobs-s-apply')]"
                ]
                
                easy_apply = None
                for selector in apply_button_selectors:
                    try:
                        easy_apply = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if easy_apply:
                            break
                    except:
                        continue
                
                if not easy_apply:
                    print("⚠️ Easy Apply button not found for this job. Skipping...")
                    continue
                
                easy_apply.click()
                print("📝 Easy Apply opened")

                time.sleep(2)

                # Wait for modal with multiple possible class names
                modal_selectors = [
                    "jobs-easy-apply-modal",
                    "jobs-apply-modal",
                    "jobs-apply-content"
                ]
                
                modal = None
                for selector in modal_selectors:
                    try:
                        modal = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, selector))
                        )
                        if modal:
                            break
                    except:
                        continue
                
                if not modal:
                    print("⚠️ Application modal not found. Skipping...")
                    continue

                # Confirm submission
                confirm = input("🚀 Submit this job application? [y/n]: ").strip().lower()
                if confirm == 'y':
                    # Look for submit button with multiple possible selectors
                    submit_selectors = [
                        ".//button[contains(., 'Submit')]",
                        ".//button[contains(., 'Submit application')]",
                        ".//button[contains(@class, 'submit-button')]"
                    ]
                    
                    submit_button = None
                    for selector in submit_selectors:
                        try:
                            submit_button = modal.find_element(By.XPATH, selector)
                            if submit_button:
                                break
                        except:
                            continue
                    
                    if submit_button:
                        submit_button.click()
                        print("✅ Application submitted!")
                        applied += 1
                    else:
                        print("⚠️ Submit button not found. Skipping...")
                
            except Exception as e:
                print(f"⚠️ Error processing job {idx+1}: {str(e)}")
                continue

    except Exception as e:
        print(f"❌ Error in job application process: {str(e)}")
        return
