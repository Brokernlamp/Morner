import time
from selenium.webdriver.common.by import By

def scrape(driver, query):
    leads = []
    url = f"https://dir.indiamart.com/search.mp?ss={query.replace(' ', '+')}"
    driver.get(url)
    time.sleep(5)

    try:
        # .lst_nm is the standard name class for IndiaMart listings
        items = driver.find_elements(By.CLASS_NAME, "lst_nm")
        for item in items:
            name = item.text.strip()
            if name:
                leads.append({"Platform": "IndiaMart", "Name": name, "Phone": "Requires Login"})
    except Exception as e:
        print(f"   ⚠️ IndiaMart Error: {e}")
    return leads