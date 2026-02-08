import json
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Import your workers
from workers import google_maps, justdial, indiamart

def extract_keyword(query):
    """Simple NLP-style keyword extractor for file naming."""
    ignore_words = ['stores', 'chennai', 'in', 'near', 'me', 'suppliers', 'wholesale', 'retailers']
    words = query.lower().split()
    keywords = [w for w in words if w not in ignore_words]
    return keywords[0] if keywords else "leads"

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def run():
    if not os.path.exists("blueprint.json"):
        print("❌ Error: blueprint.json missing!")
        return

    with open("blueprint.json", "r") as f:
        blueprint = json.load(f)

    driver = get_driver()
    all_results = []
    first_query = ""

    try:
        tasks = blueprint.get("tasks", {})
        
        for platform, queries in tasks.items():
            if not first_query and queries:
                first_query = queries[0] # Capture the first query for naming

            for q in queries:
                print(f"🚀 Scraping {platform}: {q}")
                if platform == "google_maps":
                    data = google_maps.scrape(driver, q)
                elif platform == "justdial":
                    data = justdial.scrape(driver, q)
                elif platform == "indiamart":
                    data = indiamart.scrape(driver, q)
                else:
                    data = []
                
                all_results.extend(data)

        # NLP FILE NAMING
        if all_results:
            keyword = extract_keyword(first_query)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{keyword}_{date_str}.xlsx"
            
            df = pd.DataFrame(all_results)
            df.to_excel(filename, index=False)
            print(f"\n✅ SUCCESS: {len(all_results)} leads saved to {filename}")

    finally:
        driver.quit()

if __name__ == "__main__":
    run()