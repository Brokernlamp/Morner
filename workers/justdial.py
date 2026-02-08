import time
from selenium.webdriver.common.by import By

def scrape(driver, query):
    leads = []
    # Using the list view
    url = f"https://www.justdial.com/Chennai/search?q={query.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)

    try:
        # Target the listing containers
        cards = driver.find_elements(By.CSS_SELECTOR, "div.result-content") or \
                driver.find_elements(By.CSS_SELECTOR, "li.cntanr")
        
        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, "h2").text
                leads.append({"Platform": "Justdial", "Name": name, "Phone": "Encrypted - Check Web"})
            except: continue
    except Exception as e:
        print(f"   ⚠️ Justdial Error: {e}")
    return leads