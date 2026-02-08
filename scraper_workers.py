from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

def get_driver():
    options = Options()
    # options.add_argument("--headless") # Commented out so you SEE Chrome
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

class Workers:
    @staticmethod
    def scrape_google_maps(driver, query):
        print(f"   📍 Maps Worker: Searching {query}...")
        driver.get(f"https://www.google.com/search?q={query}&tbm=lcl")
        time.sleep(5) # Wait for results
        results = driver.find_elements(By.CSS_SELECTOR, 'div.uGacc, div.VwiC3b')
        return [{"Platform": "Google Maps", "Name": r.text} for r in results if len(r.text) > 2]

    @staticmethod
    def scrape_indiamart(driver, query):
        print(f"   🏢 IndiaMart Worker: Searching {query}...")
        driver.get(f"https://dir.indiamart.com/search.mp?ss={query}")
        time.sleep(5)
        # Targeted selectors for IndiaMart listings
        results = driver.find_elements(By.CSS_SELECTOR, '.lst_nm, .m_name')
        return [{"Platform": "IndiaMart", "Name": r.text} for r in results if len(r.text) > 2]

    @staticmethod
    def scrape_olx(driver, query):
        print(f"   📦 OLX Worker: Searching {query}...")
        driver.get(f"https://www.olx.in/items/q-{query.replace(' ', '-')}")
        time.sleep(5)
        results = driver.find_elements(By.CSS_SELECTOR, '[data-aut-id="itemTitle"]')
        return [{"Platform": "OLX", "Name": r.text} for r in results if len(r.text) > 2]