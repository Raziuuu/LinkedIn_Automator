import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from automation.linkedin_automation import create_driver, load_credentials, login_linkedin
from automation.connection_requester import process_connections

if __name__ == "__main__":
    username, password = load_credentials()
    if not username or not password:
        print("Error: Could not load credentials. Please check your credentials.json file.")
        sys.exit(1)

    driver = create_driver()
    try:
        if login_linkedin(driver, username, password):
            print("Successfully logged in to LinkedIn")
            process_connections(driver, max_requests=5)
        else:
            print("Failed to log in to LinkedIn")
    finally:
        driver.quit()