from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # Enable for headless mode

driver = webdriver.Chrome(options=options)
driver.get("https://www.linkedin.com")
