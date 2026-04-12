import json
import os
import time
from playwright.sync_api import sync_playwright

CARGILLS_URLS = [
    "https://cargillsonline.com/Product/Beverages?IC=Mw==&NC=QmV2ZXJhZ2Vz",
    "https://cargillsonline.com/Product/Frozen-Food?IC=OA==&NC=RnJvemVuIEZvb2Q=",
    "https://cargillsonline.com/Product/Seeds-And-Spices?IC=MjA=&NC=U2VlZHMgJiBTcGljZXM=",
    "https://cargillsonline.com/Product/Auto-Care?IC=Mjk=&NC=QXV0byBDYXJl",
    "https://cargillsonline.com/Product/Vegetables?IC=MjM=&NC=VmVnZXRhYmxlcw==",
    "https://cargillsonline.com/Product/Food-Cupboard?IC=Nw==&NC=Rm9vZCBDdXBib2FyZA==",
    "https://cargillsonline.com/Product/Meats?IC=MTE=&NC=TWVhdHM=",
    "https://cargillsonline.com/Product/Desserts-And-Ingredients?IC=NQ==&NC=RGVzc2VydHMgJiBJbmdyZWRpZW50cw==",
    "https://cargillsonline.com/Product/Fashion?IC=NDE=&NC=RmFzaGlvbg==",
    "https://cargillsonline.com/Product/Fruits?IC=OQ==&NC=RnJ1aXRz",
    "https://cargillsonline.com/Product/Household?IC=MTA=&NC=SG91c2Vob2xk",
    "https://cargillsonline.com/Product/Seafood?IC=MTk=&NC=U2VhZm9vZA==",
    "https://cargillsonline.com/Product/Tea-And-Coffee?IC=MjE=&NC=VGVhICYgQ29mZmVl",
    "https://cargillsonline.com/Product/Health-And-Beauty?IC=NDI=&NC=SGVhbHRoICYgQmVhdXR5",
    "https://cargillsonline.com/Product/Baby-Products?IC=Mg==&NC=QmFieSBQcm9kdWN0cw==",
    "https://cargillsonline.com/Product/Cooking-Essentials?IC=NA==&NC=Q29va2luZyBFc3NlbnRpYWxz",
    "https://cargillsonline.com/Product/Snacks-And-Confectionery?IC=MTg=&NC=U25hY2tzICYgQ29uZmVjdGlvbmVyeQ==",
    "https://cargillsonline.com/Product/Pet-Products?IC=MTU=&NC=UGV0IFByb2R1Y3Rz",
    "https://cargillsonline.com/Product/Stationery?IC=MzQ=&NC=U3RhdGlvbmVyeQ==",
    "https://cargillsonline.com/Product/Dairy?IC=Ng==&NC=RGFpcnk=",
    "https://cargillsonline.com/Product/Bakery?IC=MQ==&NC=QmFrZXJ5",
    "https://cargillsonline.com/Product/Rice?IC=MTc=&NC=UmljZQ==",
    
]

JSON_FILE = 'cargills_master_data.json'

def wait_for_items_or_page(page, target_page, old_first_item_name, max_wait=60):
    """
    Hybrid Polling:
    - On Page 1: Just wait for items to exist.
    - On Page 2+: Wait for the active page number OR the first item name to change.
    """
    start_time = time.time()
    while time.time() - start_time < max_wait:
        products = page.query_selector_all(".cargillProd")
        
        if products and len(products) > 0:
            # Get data for verification
            name_el = products[0].query_selector(".veg p")
            current_first_name = name_el.inner_text().strip() if name_el else ""
            
            # Get active page from pagination UI
            active_page_el = page.query_selector("li.pagination-page.active a")
            current_page_num = active_page_el.inner_text().strip() if active_page_el else "1"

            # Case: Page 1
            if target_page == 1:
                return True, products, current_first_name
            
            # Case: Page 2+ (Hybrid Check)
            # We succeed if the UI says we are on the target page
            # OR if the first item has changed (even if the UI is slow)
            if current_page_num == str(target_page) or (current_first_name != old_first_item_name and old_first_item_name != ""):
                page.wait_for_timeout(1000) # Small buffer for Angular to finish
                return True, products, current_first_name
        
        page.wait_for_timeout(2000)
        # Nudge to keep the site responsive
        page.mouse.wheel(0, 100)
        page.mouse.wheel(0, -100)
    
    return False, [], ""

def scrape_cargills_category(page, url, seen_names, master_list):
    print(f"\n--- Scraping Category: {url} ---")
    page.goto(url, wait_until="domcontentloaded", timeout=120000)
    
    page_num = 1
    last_first_item_name = "" 

    while True:
        print(f"  Waiting for Page {page_num} products...")
        success, products, current_first_name = wait_for_items_or_page(page, page_num, last_first_item_name)
        
        if not success:
            # If polling fails, check if products are visible before giving up
            products = page.query_selector_all(".cargillProd")
            if not products:
                print(f"  No products found. Ending category at page {page_num}.")
                break
            else:
                print(f"  Wait timed out but items are visible. Proceeding with caution...")
                current_first_name = products[0].query_selector(".veg p").inner_text().strip() if products[0].query_selector(".veg p") else ""
            
        print(f"  Scraping page {page_num} ({len(products)} items found)...")
        last_first_item_name = current_first_name 

        # 2. Extract Data
        for product in products:
            try:
                name_el = product.query_selector(".veg p")
                price_el = product.query_selector(".strike1 h4")
                portion_el = product.query_selector(".dropbtn")
                
                if name_el and price_el:
                    full_name = name_el.inner_text().strip()
                    if full_name and full_name not in seen_names:
                        price_text = price_el.inner_text().replace("Rs.", "").replace(",", "").strip()
                        portion = portion_el.inner_text().strip() if portion_el else "N/A"
                        
                        master_list.append({
                            "product_name": full_name,
                            "portion": portion,
                            "price": price_text,
                            "store": "Cargills"
                        })
                        seen_names.add(full_name)
            except: continue

        # 3. Pagination Logic
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(3000)

            next_btn_li = page.locator("li.pagination-next")
            class_attr = next_btn_li.get_attribute("class") or ""
            
            if "disabled" not in class_attr:
                print(f"  Clicking Next -> Moving to Page {page_num + 1}...")
                next_btn_li.locator("a").click(force=True)
                page_num += 1
                page.wait_for_timeout(3000) # Wait for fade-out
            else:
                print(f"  Reached end of category.")
                break
        except: break

def run(playwright):
    master_list = []
    seen_names = set()
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            master_list = json.load(f)
            for item in master_list: seen_names.add(item['product_name'])
        print(f"Resuming: {len(master_list)} items already found.")

    browser = playwright.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(viewport={'width': 1366, 'height': 768})

    for url in CARGILLS_URLS:
        page = context.new_page()
        page.route("**/*.{png,jpg,jpeg,svg,webp}", lambda route: route.abort())
        try:
            scrape_cargills_category(page, url, seen_names, master_list)
        except Exception as e:
            print(f"  Category Error: {e}")
        
        page.close()
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_list, f, indent=4)
        print(f"  Progress saved. Total items: {len(master_list)}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)