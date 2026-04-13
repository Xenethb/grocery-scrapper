import json
import re
from supabase import create_client, Client

# Your Supabase credentials
URL = "https://ykbiztlpwzhcrmoorjhj.supabase.co"
KEY = "sb_publishable_ApsMD3_odkTfRIGPzZ2DEw_ZpyOadi0" 

supabase: Client = create_client(URL, KEY)

def clean_price(price_value):
    """Extracts the first decimal number from a string."""
    if price_value is None or price_value == "":
        return None
    price_str = str(price_value)
    match = re.search(r"(\d+\.\d+|\d+)", price_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def clear_products_table():
    """Wipes all rows from the products table before starting."""
    print("🧹 Clearing existing data from the products table...")
    try:
        # We use .gt("id", 0) because Supabase requires a filter for delete
        supabase.table("products").delete().gt("id", 0).execute()
        print("✨ Table cleared successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear table (it might already be empty): {e}")

def upload_in_batches(data, batch_size=50):
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            formatted_batch = []
            for item in batch:
                formatted_batch.append({
                    "name": item["name"],
                    "glomark_price": clean_price(item.get("glomark_price")),
                    "keells_price": clean_price(item.get("keells_price")),
                    "cargills_price": clean_price(item.get("cargills_price"))
                })
            
            supabase.table("products").insert(formatted_batch).execute()
            print(f"✅ Successfully uploaded items {i} to {i + len(batch)}")
        except Exception as e:
            print(f"❌ Error in batch starting at {i}: {e}")

# Main execution
if __name__ == "__main__":
    try:
        with open('master_comparison.json', 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        # --- Step 1: Wipe the table ---
        clear_products_table()
        
        # --- Step 2: Upload new data ---
        print(f"🚀 Starting cleaned upload for {len(full_data)} items...")
        upload_in_batches(full_data)
        
        print("\n🎉 All done! Your Supabase database is fresh and updated.")
        
    except FileNotFoundError:
        print("Error: 'master_comparison.json' not found. Run merge_groceries.py first!")