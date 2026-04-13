import json
import time
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

# Your Supabase Credentials
URL = "https://ykbiztlpwzhcrmoorjhj.supabase.co"
KEY = "sb_publishable_ApsMD3_odkTfRIGPzZ2DEw_ZpyOadi0" 
supabase: Client = create_client(URL, KEY)

def scrape_glomark_locations(page):
    print("📍 Scraping Glomark Locations...")
    page.goto("https://glomark.lk/store-locator", wait_until="networkidle")
    # Glomark often stores data in a window variable or within the map scripts
    stores = page.evaluate("""() => {
        // This is a common pattern for stores using map markers
        return typeof all_locations !== 'undefined' ? all_locations : []; 
    }""")
    
    # Backup: If no variable, we scrape the list items if visible
    if not stores:
        elements = page.query_selector_all(".store-location-item") # Adjust based on actual UI
        # ... fallback logic ...
    
    return [{"chain": "Glomark", "name": s.get('name'), "lat": s.get('lat'), "lng": s.get('lng'), "addr": s.get('address')} for s in stores]

def scrape_keells_locations(page):
    print("📍 Scraping Keells Locations...")
    page.goto("https://www.keellssuper.com/store-locator", wait_until="networkidle")
    # Keells uses an API call in the background usually. 
    # We can wait for the response or grab the rendered list.
    page.wait_for_selector(".store-locator-list-item")
    stores = page.evaluate("""() => {
        let items = [];
        document.querySelectorAll('.store-locator-list-item').forEach(el => {
            items.append({
                name: el.querySelector('.store-name').innerText,
                address: el.querySelector('.store-address').innerText,
                lat: el.getAttribute('data-lat'),
                lng: el.getAttribute('data-lng')
            });
        });
        return items;
    }""")
    return [{"chain": "Keells", "name": s['name'], "lat": float(s['lat']), "lng": float(s['lng']), "addr": s['address']} for s in stores]

# (Similarly for Cargills...)

def upload_locations(locations):
    print(f"🚀 Uploading {len(locations)} store locations to Supabase...")
    for loc in locations:
        supabase.table("store_locations").insert({
            "store_chain": loc['chain'],
            "branch_name": loc['name'],
            "latitude": loc['lat'],
            "longitude": loc['lng'],
            "address": loc['addr']
        }).execute()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Note: These websites change frequently. 
    # If the selectors fail, we can manually grab their store list JSON.
    all_locs = []
    try:
        all_locs.extend(scrape_glomark_locations(page))
        # all_locs.extend(scrape_keells_locations(page))
    except Exception as e:
        print(f"Scrape Error: {e}")
        
    if all_locs:
        upload_locations(all_locs)
    
    browser.close()