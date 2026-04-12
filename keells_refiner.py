import json
import os
import time
from playwright.sync_api import sync_playwright

TARGET_URLS = [
    "https://www.keellssuper.com/beverages",
    "https://www.keellssuper.com/grocery",
    "https://www.keellssuper.com/electronic-devices",
    "https://www.keellssuper.com/household-essentials"
]

JSON_FILE = 'keells_master_data.json'

def wait_for_products_to_change(page, old_first_item, max_wait=120):
    """
    Polls the page every 2 seconds to see if the content has actually changed.
    If it changes, we break out early and move to the next step.
    """
    start_time = time.time()
    print(f"    [Polling] Waiting for page content to update (Max {max_wait}s)...")
    
    while time.time() - start_time < max_wait:
        # 1. Nudge the page to trigger React rendering
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(2000) # Small pause between checks
        
        # 2. Grab current products
        current_products = page.query_selector_all(".product-card-containerV2")
        
        if current_products:
            current_first_item = current_products[0].inner_text().strip()
            # If we see items and the first item is different from the previous page, we are ready!
            if current_first_item != old_first_item:
                print(f"    [Success] Content updated in {int(time.time() - start_time)} seconds.")
                return True, current_products
        
    return False, []

def scrape_heavy_category(page, url, seen_names, master_list):
    print(f"\n--- Starting Smart Scrape: {url} ---")
    
    # 1. Initial Load - Smart wait for structure
    page.goto(url, wait_until="domcontentloaded", timeout=180000)
    
    # 2. Smart wait for 'View All' (Timeout of 120s, but moves on as soon as it appears)
    try:
        view_all_selector = "button.btn-success:has-text('View All')"
        view_all_btn = page.wait_for_selector(view_all_selector, state="visible", timeout=120000)
        
        if view_all_btn:
            view_all_btn.scroll_into_view_if_needed()
            view_all_btn.click()
            print("  Clicked 'View All'.")
            # Wait for the "Reset" after View All (Old items disappear, new ones appear)
            page.wait_for_timeout(5000) 
    except:
        print("  'View All' not found within 120s. Proceeding with current view.")

    page_num = 1
    last_first_item_name = ""

    while True:
        # 3. Dynamic wait for items to appear on THIS page
        success, products = wait_for_products_to_change(page, last_first_item_name)

        if not success or not products:
            print(f"  Stopped: Content did not load or change after massive wait at page {page_num}.")
            break
            
        print(f"  Scraping page {page_num} ({len(products)} items)...")
        
        # 4. Extract data
        # Store the first item name so we can verify the next page change
        last_first_item_name = products[0].inner_text().strip()
        
        for product in products:
            try:
                name_el = product.query_selector(".product-card-nameV2")
                price_el = product.query_selector(".product-card-final-priceV2")
                if name_el and price_el:
                    full_name = name_el.inner_text().strip()
                    if full_name not in seen_names:
                        price_text = price_el.inner_text().split('/')[0]
                        clean_price = "".join(filter(lambda x: x.isdigit() or x == '.', price_text))
                        master_list.append({"product_name": full_name, "price": clean_price, "store": "Keells"})
                        seen_names.add(full_name)
            except: continue

        # 5. Handle Pagination
        try:
            next_btn = page.locator("button.page-number-button-arrow").filter(has=page.locator("img[src*='Right Arrow']"))
            if next_btn.is_visible(timeout=5000) and next_btn.is_enabled():
                next_btn.click()
                print(f"  Clicked Next. Moving to page {page_num + 1}...")
                page_num += 1
                # The loop will now return to the top and run wait_for_products_to_change()
            else:
                print("  Reached the end of the category.")
                break
        except:
            break

def run(playwright):
    master_list = []
    seen_names = set()
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            master_list = json.load(f)
            for item in master_list: seen_names.add(item['product_name'])
        print(f"Resuming with {len(master_list)} items.")

    browser = playwright.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(viewport={'width': 1366, 'height': 768})

    for url in TARGET_URLS:
        page = context.new_page()
        # Ensure icons aren't blocked so robot can "see" buttons
        page.route("**/*.{png,jpg,jpeg,svg,webp}", lambda route: 
                   route.continue_() if "Arrow" in route.request.url or "ea9baf5b" in route.request.url else route.abort())
        
        try:
            scrape_heavy_category(page, url, seen_names, master_list)
        except Exception as e:
            print(f"  Error on {url}: {e}")
        
        page.close()
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_list, f, indent=4)
        print(f"  Total items saved: {len(master_list)}")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)