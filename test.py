import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--file", default="export.csv")
args = parser.parse_args()

DIGIT_MAP = {
    "icon-acb": "0", "icon-yz": "1", "icon-wx": "2", "icon-vu": "3",
    "icon-ts": "4", "icon-rq": "5", "icon-po": "6", "icon-nm": "7",
    "icon-lk": "8", "icon-ji": "9"
}

def decode_phone(card):
    phone = ""
    spans = card.find_elements(By.XPATH, ".//span[contains(@class,'mobilesv')]//span")
    for sp in spans:
        cls = sp.get_attribute("class")
        if cls in DIGIT_MAP:
            phone += DIGIT_MAP[cls]
    return phone or "-"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(args.url)
time.sleep(5)

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

cards = driver.find_elements(By.XPATH, "//div[contains(@class,'resultbox')]")
print("Found:", len(cards))

rows = []

for card in cards:
    try:
        name = card.find_element(By.CLASS_NAME, "lng_cont_name").text
    except:
        name = "-"

    try:
        address = card.find_element(By.CLASS_NAME, "cont_fl_addr").text
    except:
        address = "-"

    phone = decode_phone(card)

    rows.append({
        "Name": name,
        "Address": address,
        "Phone": phone
    })

driver.quit()

pd.DataFrame(rows).to_csv(args.file, index=False)
print("Saved to", args.file)
