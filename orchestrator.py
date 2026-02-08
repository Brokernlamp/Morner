import json
import os
import pandas as pd
from scraper_workers import Workers, get_driver

def run_orchestrator():
    print("\n" + "═"*60)
    print(" 🚀  MASTER AI SCRAPER ORCHESTRATOR  ".center(60))
    print("═"*60)

    # 1. Load the Blueprint
    if not os.path.exists("blueprint.json"):
        print("❌ Error: blueprint.json not found!")
        return

    with open("blueprint.json", "r") as f:
        blueprint = json.load(f)

    tasks = blueprint.get("tasks", {})
    all_leads = []

    # 2. Initialize Browser once
    driver = get_driver()
    
    try:
        # 3. Dynamic Platform Execution
        for platform, queries in tasks.items():
            print(f"\n🔹 Activating Worker for: {platform.upper()}")
            
            for q in queries:
                if platform == "google_maps":
                    data = Workers.scrape_google_maps(driver, q)
                elif platform == "indiamart":
                    data = Workers.scrape_indiamart(driver, q)
                elif platform == "olx":
                    data = Workers.scrape_olx(driver, q)
                else:
                    print(f"⚠️ No worker configured for {platform}")
                    data = []
                
                all_leads.extend(data)
                print(f"   ✅ Found {len(data)} potential leads.")

        # 4. Save Results
        if all_leads:
            df = pd.DataFrame(all_leads)
            df.to_excel("Master_Leads_List.xlsx", index=False)
            print(f"\n🎉 DONE! {len(all_leads)} leads saved to Master_Leads_List.xlsx")
        else:
            print("\n⚠️ Orchestrator finished but no data was captured.")

    finally:
        print("\nShutting down in 10 seconds...")
        import time
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    run_orchestrator()