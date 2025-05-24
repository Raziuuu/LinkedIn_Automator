import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

from automation.linkedin_automation import create_driver, login_linkedin, load_credentials
from automation.alumni_messenger import run_alumni_outreach

if __name__ == "__main__":
    # Load credentials
    creds = load_credentials()
    
    # Create and configure the driver
    driver = create_driver()

    print("🔐 Launching browser with existing Chrome profile...")
    if not login_linkedin(driver, creds["username"], creds["password"]):
        print("❌ Login failed. Exiting.")
        driver.quit()
        exit()

    # Start messaging alumni
    run_alumni_outreach(driver)

    # Clean up
    driver.quit()