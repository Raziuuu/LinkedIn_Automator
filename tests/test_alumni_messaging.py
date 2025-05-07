import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(project_root))

from automation.linkedin_automation import create_driver, login_linkedin, load_credentials
from automation.alumni_messenger import message_alumni

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

    # Input Details
    college = input("🏫 Enter your college name: ").strip()
    department = input("🏬 Enter your department/major: ").strip()
    year = input("🎓 Enter your graduation year: ").strip()
    resume_path = input("📄 Enter full path to your resume file (PDF): ").strip()
    purpose = input("✉️ Reason for messaging (e.g., 'connect', 'seek guidance', 'job help'): ").strip()

    # Validate resume file
    if not os.path.isfile(resume_path):
        print("❌ Invalid resume file path. Exiting.")
        driver.quit()
        exit()

    # Start messaging alumni
    message_alumni(driver, college, department, year, resume_path, purpose)

    # Clean up
    driver.quit()
