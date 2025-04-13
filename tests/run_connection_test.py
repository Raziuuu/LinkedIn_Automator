import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from automation.linkedin_automation import create_driver, load_credentials, login_linkedin
from automation.connection_requester import process_connections

if __name__ == "__main__":
    creds = load_credentials()
    driver = create_driver()

    if login_linkedin(driver, creds["username"], creds["password"]):
        process_connections(driver, max_requests=5)

    driver.quit()
