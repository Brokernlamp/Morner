import os
import json
import time
import pandas as pd
from datetime import datetime
from multiprocessing import Process, Manager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Dynamic imports
from strategy import StrategyEngine
from workers import google_maps, justdial, indiamart

def get_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_keyword(query):
    ignore = ['stores', 'chennai', 'india', 'wholesale', 'suppliers', 'retailers', 'in', 'near']
    words = query.lower().split()
    clean = [w for w in words if w not in ignore]
    return clean[0] if clean else "leads"

def run_worker_core(platform, queries, shared_results, is_headless):
    """Worker process for parallel execution."""
    print(f"🔥 [PARALLEL START] {platform.upper()} core is launching...")
    driver = get_driver(headless=is_headless)
    
    try:
        platform_data = []
        for q in queries:
            if platform == "google_maps":
                data = google_maps.scrape(driver, q)
            elif platform == "justdial":
                data = justdial.scrape(driver, q)
            elif platform == "indiamart":
                data = indiamart.scrape(driver, q)
            else:
                data = []
            
            platform_data.extend(data)
            # Show progress per query
            print(f"   ✨ {platform.upper()} finished: '{q}' -> Found {len(data)}")
        
        shared_results.extend(platform_data)
        
    except Exception as e:
        print(f"❌ [CORE ERROR] {platform.upper()} failed: {e}")
    finally:
        driver.quit()

def main():
    print("\n" + "═"*60)
    print(" 🤖  PURE PARALLEL AI LEAD ORCHESTRATOR (V3.1) ".center(60))
    print("═"*60)
    
    # --- PHASE 1: INPUTS ---
    offering = input("📦 What are you offering?: ")
    location = input("📍 Location: ")
    print("\n🏢 Business Size: (1) Small (2) Medium (3) Enterprise")
    size_choice = input("   Select: ")
    size_map = {"1": "Small", "2": "Medium", "3": "Large"}
    persona = input("👤 Target Decision Maker: ")

    # --- PHASE 2: AI STRATEGY ---
    print("\n🧠 AI: Analyzing niche and selecting platforms...")
    engine = StrategyEngine()
    blueprint = engine.get_search_blueprint({
        "offering": offering,
        "location": location,
        "target_size": size_map.get(size_choice, "Medium"),
        "decision_maker": persona
    })

    tasks = blueprint.get("tasks", {})
    if not tasks:
        print("❌ AI determined no suitable platforms.")
        return

    # --- NEW: SEARCH PARAMETER VISIBILITY ---
    print("\n" + "─"*60)
    print("📋 STRATEGIC ROADMAP (Search Parameters)")
    print("─"*60)
    for platform, queries in tasks.items():
        print(f"🌐 {platform.upper()}:")
        for i, q in enumerate(queries, 1):
            print(f"   {i}. {q}")
    print("─"*60)

    # --- PHASE 3: PARALLEL EXECUTION ---
    print("\n⚙️ Mode: (1) Visual (2) Fast/Headless")
    is_headless = True if input("   Select: ") == "2" else False

    confirm = input(f"\n🚀 Ready to launch {len(tasks)} workers? (y/n): ").lower()
    if confirm != 'y': return

    with Manager() as manager:
        shared_results = manager.list()
        processes = []

        for platform, queries in tasks.items():
            p = Process(target=run_worker_core, args=(platform, queries, shared_results, is_headless))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        # --- PHASE 4: CONSOLIDATION ---
        final_leads = list(shared_results)
        if final_leads:
            first_q = list(tasks.values())[0][0]
            filename = f"{extract_keyword(first_q)}_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
            pd.DataFrame(final_leads).to_excel(filename, index=False)
            print("\n" + "═"*60)
            print(f"🎉 SUCCESS! {len(final_leads)} leads saved to {filename}")
            print("═"*60)

if __name__ == "__main__":
    main()