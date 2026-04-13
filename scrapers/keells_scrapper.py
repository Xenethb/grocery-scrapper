import json
import time
from playwright.sync_api import sync_playwright

KEELLS_URLS = [
    "https://www.keellssuper.com/fresh-vegetables",
    "https://www.keellssuper.com/fresh-fruits",
    "https://www.keellssuper.com/keells-meat-shop",
    "https://www.keellssuper.com/fresh-fish",
    "https://www.keellssuper.com/beverages",
    "https://www.keellssuper.com/chilled-products",
    "https://www.keellssuper.com/frozen-food",
    "https://www.keellssuper.com/grocery",
    "https://www.keellssuper.com/household-essentials",
    "https://www.keellssuper.com/hampers-and-vouchers",
    "https://www.keellssuper.com/keells-bakery",
    "https://www.keellssuper.com/electronic-devices"
]

def scrape_keells_category(page, url, seen_names, master_list):
    print(f"\n--- Opening: {url} ---")
    
    try:
        # 1. Wait for a full 2 minutes if necessary for the base page
        page.goto(url, wait_until="load", timeout=120000)
        
        # 2. INCREASED: 15 seconds hard wait just to let the React scripts settle
        print("  Waiting 15s for initial scripts to settle...")
        page.wait_for_timeout(30000) 
    except Exception as e:
        print(f"  Initial load took too long: {e}. Trying to proceed...")

    # 3. Handle 'View All' with a much longer patience
    try:
        view_all_selector = "button.btn-success:has-text('View All')"
        # Wait up to 20 seconds for the button to even appear
        view_all_btn = page.wait_for_selector(view_all_selector, state="visible", timeout=30000)
        if view_all_btn:
            view_all_btn.click()
            print("  Clicked 'View All' - Waiting 15s for massive list reload...")
            # INCREASED: Give it 15 seconds to load the entire category
            page.wait_for_timeout(30000) 
    except:
        print("  'View All' not found or timed out. Using standard pagination.")

    page_num = 1
    while True:
        # 4. Check & Retry for products
        # We try 4 times, waiting 10 seconds between each.
        products = []
        for attempt in range(4):
            # Scroll down and up to "wake up" the image/data loaders
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(2000)
            page.mouse.wheel(0, -500)
            
            products = page.query_selector_all(".product-card-containerV2")
            if products:
                break
            print(f"  (Attempt {attempt+1}) No products visible yet. Waiting 10s...")
            page.wait_for_timeout(30000) 

        if not products:
            print("  Stopping: No products found after multiple long attempts.")
            break
            
        print(f"  Scraping page {page_num} ({len(products)} items found)...")
        
        for product in products:
            try:
                name_el = product.query_selector(".product-card-nameV2")
                price_el = product.query_selector(".product-card-final-priceV2")
                
                if name_el and price_el:
                    full_name = name_el.inner_text().strip()
                    if full_name and full_name not in seen_names:
                        price_text = price_el.inner_text().split('/')[0]
                        clean_price = "".join(filter(lambda x: x.isdigit() or x == '.', price_text))
                        
                        master_list.append({
                            "product_name": full_name,
                            "price": clean_price,
                            "store": "Keells"
                        })
                        seen_names.add(full_name)
            except:
                continue # Skip a single bad product card

        # 5. Long-Wait Pagination
        try:
            next_btn = page.locator("button.page-number-button-arrow").filter(has=page.locator("img[src*='Right Arrow']"))
            
            if next_btn.is_visible(timeout=5000) and next_btn.is_enabled():
                next_btn.click()
                print(f"  Turning to page {page_num + 1}... Waiting 10s for load.")
                page_num += 1
                # INCREASED: Wait 10s for the next page to fully render
                page.wait_for_timeout(30000) 
            else:
                print("  End of category reached.")
                break
        except:
            break

def run(playwright):
    # Added a slightly longer slow_mo to be very gentle with the site
    browser = playwright.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(viewport={'width': 1366, 'height': 768})
    
    seen_names = set()
    master_list = []

    # Process one URL at a time
    for url in KEELLS_URLS:
        # Create a fresh page for EVERY category to prevent memory leaks or crashes
        page = context.new_page()
        page.set_default_timeout(70000)
        
        # Block images but keep arrows
        page.route("**/*.{png,jpg,jpeg,svg,webp}", lambda route: 
                   route.continue_() if "Arrow" in route.request.url else route.abort())
        
        try:
            scrape_keells_category(page, url, seen_names, master_list)
        except Exception as e:
            print(f"  Category {url} failed: {e}")
        
        # Close the page before starting the next one to keep the browser clean
        page.close()

    # Save to JSON
    with open('keells_master_data.json', 'w', encoding='utf-8') as f:
        json.dump(master_list, f, indent=4)

    print(f"\nFINISHED! Total Unique Products: {len(master_list)}")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)