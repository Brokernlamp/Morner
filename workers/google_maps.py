import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape(driver, query):
    leads = []
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    driver.get(url)
    
    try:
        # Wait for listings to appear
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
        
        # Get all listing anchors
        results = driver.find_elements(By.CLASS_NAME, "hfpxzc")

        for i in range(min(len(results), 10)):  # Limit to top 10 for speed
            try:
                # Re-find elements to avoid "StaleElementReferenceException"
                items = driver.find_elements(By.CLASS_NAME, "hfpxzc")
                name = items[i].get_attribute("aria-label")
                
                # CLICK the business to open the details panel
                items[i].click()
                time.sleep(3) # Wait for panel to load

                # Scrape phone number from the panel
                # This XPATH looks for the specific "Phone" icon/text area
                phone = "Not Found"
                try:
                    phone_el = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone")]')
                    phone = phone_el.get_attribute("aria-label").replace("Phone: ", "")
                except:
                    pass

                leads.append({
                    "Platform": "Google Maps",
                    "Name": name,
                    "Phone": phone,
                    "Query": query
                })
            except Exception as e:
                continue
    except Exception as e:
        print(f"   ⚠️ Maps Error: {e}")
    return leads