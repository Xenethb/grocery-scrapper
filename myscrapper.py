import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://glomark.lk"

def scrape_category(page, url, seen_names, master_list):
    """Scrapes a single category page with increased wait times and scrolling."""
    print(f"\n--- Scraping Category: {url} ---")
    
    # 1. Navigate with a longer timeout and wait for the network to be quiet
    page.goto(url, wait_until="networkidle", timeout=60000)
    
    # 2. Initial wait to ensure product boxes are present
    try:
        page.wait_for_selector(".product-box", timeout=10000)
    except:
        print(f"  Warning: No products found on initial load for {url}")
        return

    # 3. Click 'Show More' Loop
    while True:
        try:
            # Scroll to the bottom to make sure the button is triggered/visible
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000) # Small pause after scroll

            # Look for the 'Show More' button with a longer wait (5 seconds)
            show_more = page.wait_for_selector("button.see_more_btn_all", timeout=5000)
            
            if show_more and show_more.is_visible():
                show_more.click()
                print("  Clicked Show More (Loading more items...)")
                # INCREASED: Give the site 3.5 seconds to load the next batch of data
                page.wait_for_timeout(3500) 
            else:
                break
        except:
            # If button disappears or isn't found within 5s, we are done
            break

    # 4. Extract unique products after everything is loaded
    products = page.query_selector_all(".product-box")
    new_items_count = 0
    
    for product in products:
        name_el = product.query_selector(".product-title")
        price_el = product.query_selector(".price")
        
        if name_el and price_el:
            full_name = name_el.inner_text().strip()
            
            if full_name not in seen_names:
                raw_price = price_el.inner_text().replace("Rs", "").replace(",", "").strip()
                # Clean any extra spaces or symbols from price
                clean_price = "".join(filter(lambda x: x.isdigit() or x == '.', raw_price))
                
                parts = full_name.split()
                portion = parts[-1] if len(parts) > 1 else "N/A"

                master_list.append({
                    "product_name": full_name,
                    "portion": portion,
                    "price": clean_price,
                    "store": "Glomark"
                })
                seen_names.add(full_name)
                new_items_count += 1
                
    print(f"  Finished category. Added {new_items_count} new unique items.")

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Block images to save your mobile data
    page.route("**/*.{png,jpg,jpeg,svg,webp}", lambda route: route.abort())

    print("Opening Glomark home page...")
    page.goto(BASE_URL, wait_until="networkidle")
    
    # Open Side Menu
    try:
        page.wait_for_selector(".navbar-toggle-icon", timeout=10000)
        page.click(".navbar-toggle-icon")
        page.wait_for_timeout(1500)
    except:
        print("Menu toggle not found, continuing...")

    # Discover Category Links
    category_links = []
    all_links = page.query_selector_all("a[href*='/dp/']")
    
    for link in all_links:
        href = link.get_attribute("href")
        if href:
            full_url = BASE_URL + href if href.startswith("/") else href
            if full_url not in category_links:
                category_links.append(full_url)

    print(f"Found {len(category_links)} categories.")

    seen_names = set()
    master_list = []

    # Scraping Loop
    for url in category_links:
        scrape_category(page, url, seen_names, master_list)

    # Save to Master JSON
    with open('glomark_master_data.json', 'w', encoding='utf-8') as f:
        json.dump(master_list, f, indent=4)

    print(f"\nSUCCESS! Total Unique Products Scraped: {len(master_list)}")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)