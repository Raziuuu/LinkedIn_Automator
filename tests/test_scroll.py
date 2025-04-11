# test_scroll.py

import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from automation.linkedin_automation import start_login_process, create_driver, load_credentials, login_linkedin
from automation.feed_scroller import engage_feed

if __name__ == "__main__":
    creds = load_credentials()
    driver = create_driver()

    if login_linkedin(driver, creds["username"], creds["password"]):
        engage_feed(driver)

    driver.quit()
