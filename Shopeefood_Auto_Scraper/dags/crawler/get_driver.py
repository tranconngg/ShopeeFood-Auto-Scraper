from selenium import webdriver
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--headless")
    driver = webdriver.Remote(
        command_executor="http://hub:4444/wd/hub", options=options
    )
    return driver
