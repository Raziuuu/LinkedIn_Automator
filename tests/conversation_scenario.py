import os
import sys
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from automation.linkedin_automation import create_driver, load_credentials, login_linkedin
from automation.message_bot import start_bulk_messaging
from automation.connection_requester import process_connections
from automation.feed_scroller import engage_feed
import time

def test_full_conversational_flow():
    print("\n🚀 Starting Day 10: Full Conversational AI Scenario Testing...")

    # Step 1: Setup & Login
    creds = load_credentials()
    driver = create_driver()

    if not login_linkedin(driver, creds["username"], creds["password"]):
        print("❌ Login failed. Aborting test.")
        driver.quit()
        return

    print("\n✅ Step 1: Logged in successfully")

    # Step 2: Messaging Test
    print("\n💬 Step 2: Messaging Scenario Test")
    try:
        start_bulk_messaging(driver)
    except Exception as e:
        print(f"⚠️ Messaging flow failed: {e}")

    # Step 3: Connection Test
    print("\n🤝 Step 3: Connection Request Scenario Test")
    try:
        process_connections(driver, max_requests=2)
    except Exception as e:
        print(f"⚠️ Connection flow failed: {e}")

    # Step 4: Feed Engagement Test
    print("\n📰 Step 4: Feed Engagement Scenario Test")
    try:
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(5)
        engage_feed(driver, max_posts=3)
    except Exception as e:
        print(f"⚠️ Feed flow failed: {e}")

    # Step 5: Close driver
    driver.quit()
    print("\n🎯 Day 10 Test Completed – All Flows Executed in Single Session")

# Entry point
if __name__ == "__main__":
    test_full_conversational_flow()
