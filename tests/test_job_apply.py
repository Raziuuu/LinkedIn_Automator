import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.linkedin_automation import create_driver, login_linkedin, load_credentials
from automation.job_applicator import apply_for_jobs

if __name__ == "__main__":
    # Load credentials
    creds = load_credentials()
    
    # Create and configure the driver
    driver = create_driver()
    
    # Login with credentials
    if login_linkedin(driver, creds["username"], creds["password"]):
        apply_for_jobs(driver)
    else:
        print("❌ Login failed. Exiting.")

    driver.quit()
