import json
import pandas as pd
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class ScraperEngine:
    def __init__(self):
        # SETTING UP THE BROWSER
        chrome_options = Options()
        # WE ARE NOT ADDING --headless HERE, SO YOU WILL SEE THE BROWSER
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    def scrape_google_maps(self, query):
        print(f"   📍 Maps Worker: Searching for '{query}'...")
        leads = []
        url = f"https://www.google.com/search?q={query}&tbm=lcl"
        
        self.driver.get(url)
        time.sleep(random.uniform(5, 7)) # Wait for you to see it!

        # Extract names from the visible Chrome window
        elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.uGacc, div.VwiC3b')
        for el in elements:
            name = el.text.strip()
            if len(name) > 3:
                leads.append({
                    "Platform": "Google Maps",
                    "Name": name,
                    "Location": "Detected from Browser"
                })
        return leads

    def quit(self):
        self.driver.quit()

def main():
    print("\n" + "="*60)
    print(" ⚙️  TOOL 2: SELENIUM VISUAL SCRAPER ".center(60))
    print("="*60)

    if not os.path.exists("blueprint.json"):
        print("❌ Error: blueprint.json not found.")
        return

    with open("blueprint.json", "r") as f:
        blueprint = json.load(f)

    tasks = blueprint.get("tasks", {})
    all_data = []
    engine = ScraperEngine()
    
    try:
        if "google_maps" in tasks:
            for q in tasks["google_maps"]:
                data = engine.scrape_google_maps(q)
                all_data.extend(data)

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel("Final_Leads_Database.xlsx", index=False)
            print(f"✅ SUCCESS! Saved {len(all_data)} leads.")
        else:
            print("⚠️ Still no data. Check the Chrome window for a CAPTCHA!")
            
    finally:
        input("Press Enter to close the browser...")
        engine.quit()

if __name__ == "__main__":
    main()