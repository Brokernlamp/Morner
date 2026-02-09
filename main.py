import os
import time
import pandas as pd
from datetime import datetime
from multiprocessing import Process, Manager, Lock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Dynamic imports
from strategy import StrategyEngine
from workers import google_maps, general_web

def get_driver(driver_path, port_id, headless=False):
    """Initializes Chrome with a unique port to avoid macOS socket collisions."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # 🛠️ UNIQUE PORT OFFSET: Worker 0 gets 9515, Worker 1 gets 9516...
    # This is the "Silver Bullet" for the 'Can not connect' error on Mac.
    service = Service(executable_path=driver_path, port=9515 + port_id)
    return webdriver.Chrome(service=service, options=options)

def extract_keyword(query):
    """Shortens the filename based on the primary search term."""
    ignore = ['stores', 'pune', 'india', 'wholesale', 'suppliers', 'retailers', 'in', 'near', 'services']
    words = query.lower().split()
    clean = [w for w in words if w not in ignore]
    return clean[0] if clean else "leads"

def run_worker_core(platform, queries, shared_results, is_headless, print_lock, driver_path, worker_id):
    """Worker logic with parallel tab support and port isolation."""
    start_time = datetime.now().strftime("%H:%M:%S")
    with print_lock:
        print(f"🚀 [{start_time}] [{platform.upper()}] Initializing Core (Port: {9515 + worker_id})")
    
    driver = None
    try:
        driver = get_driver(driver_path, worker_id, headless=is_headless)
        
        # --- PHASE 1: PARALLEL TAB SETUP ---
        for i, q in enumerate(queries):
            if i > 0:
                driver.execute_script("window.open('');")
            
            driver.switch_to.window(driver.window_handles[i])
            
            # Map platform to specific search URLs
            url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
            if platform == "google_maps":
                url = f"https://www.google.com/maps/search/{q.replace(' ', '+')}"
            
            driver.get(url)
            with print_lock:
                print(f"📡 [{platform.upper()}] Tab {i+1} Loaded: '{q}'")

        # Allow tabs to settle
        time.sleep(5)

        # --- PHASE 2: DATA EXTRACTION ---
        for i, q in enumerate(queries):
            driver.switch_to.window(driver.window_handles[i])
            
            data = []
            if platform == "google_maps":
                data = google_maps.scrape(driver, q)
            elif platform == "general_web":
                data = general_web.scrape(driver, q)
            
            shared_results.extend(data)
            now = datetime.now().strftime("%H:%M:%S")
            with print_lock:
                print(f"✅ [{now}] [{platform.upper()}] Tab {i+1} Scraped ({len(data)} leads)")

    except Exception as e:
        with print_lock:
            print(f"⚠️ [{platform.upper()}] Process Error: {e}")
    finally:
        if driver:
            driver.quit()

def main():
    print("\n" + "═"*60)
    print(" 🤖  PURE PARALLEL AI LEAD ORCHESTRATOR (V3.5) ".center(60))
    print("═"*60)
    
    # --- PHASE 1: INPUTS ---
    offering = input("📦 What are you offering?: ")
    location = input("📍 Location: ")
    print("\n🏢 Business Size: (1) Small (2) Medium (3) Enterprise")
    size_choice = input("   Select: ")
    size_map = {"1": "Small", "2": "Medium", "3": "Large"}
    persona = input("👤 Target Decision Maker: ")

    # --- PHASE 2: AI STRATEGY & DRIVER PRE-FETCH ---
    print("\n🧠 AI: Analyzing market and formulating strategy...")
    engine = StrategyEngine()
    blueprint = engine.get_search_blueprint({
        "offering": offering, "location": location,
        "target_size": size_map.get(size_choice, "Medium"),
        "decision_maker": persona
    })

    tasks = blueprint.get("tasks", {})
    if not tasks:
        print("❌ AI failed to provide a valid task blueprint.")
        return

    # Install driver ONCE in main thread to avoid Race Conditions
    print("🔧 Pre-loading verified WebDriver...")
    raw_path = ChromeDriverManager().install()
    driver_path = raw_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver") if "THIRD_PARTY_NOTICES" in raw_path else raw_path

    # --- PHASE 3: PARALLEL EXECUTION ---
    print("\n⚙️ Execution Mode: (1) Visual (2) Headless")
    is_headless = True if input("   Select: ") == "2" else False

    confirm = input(f"\n🚀 Launch {len(tasks)} parallel workers? (y/n): ").lower()
    if confirm != 'y': return

    with Manager() as manager:
        shared_results = manager.list()
        print_lock = Lock()
        processes = []

        try:
            # Stagger launch by ID to assign unique ports
            for worker_id, (platform, queries) in enumerate(tasks.items()):
                if platform in ["google_maps", "general_web"]:
                    p = Process(target=run_worker_core, 
                                args=(platform, queries, shared_results, is_headless, print_lock, driver_path, worker_id))
                    processes.append(p)
                    p.start()
                    time.sleep(4) # Stagger prevents Port/Socket collisions on Mac

            for p in processes:
                p.join()

        except KeyboardInterrupt:
            print("\n\n🛑 [INTERRUPT] Caught Ctrl+C. Preserving shared memory buffer...")
            for p in processes:
                p.terminate()

        # --- PHASE 4: CONSOLIDATION (Always runs) ---
        final_leads = list(shared_results)
        if final_leads:
            # Generate a dynamic filename based on the first query keyword
            first_q = list(tasks.values())[0][0]
            filename = f"leads_{extract_keyword(first_q)}_{datetime.now().strftime('%H-%M')}.xlsx"
            
            df = pd.DataFrame(final_leads)
            if "Name" in df.columns:
                df = df.drop_duplicates(subset=["Name"])
            
            df.to_excel(filename, index=False)
            print("\n" + "═"*60)
            print(f"🎉 MISSION SUCCESS! {len(df)} leads saved to {filename}")
            print("═"*60)
        else:
            print("\n⚠️ No leads collected.")

if __name__ == "__main__":
    main()
