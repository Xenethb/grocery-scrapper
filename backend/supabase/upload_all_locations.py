import json
import os
from supabase import create_client, Client

# --- CONFIGURATION ---
URL = "https://ykbiztlpwzhcrmoorjhj.supabase.co"
KEY = "sb_publishable_ApsMD3_odkTfRIGPzZ2DEw_ZpyOadi0" 
supabase: Client = create_client(URL, KEY)

# 1. Your raw Glomark data
glomark_raw = [
    {"name":"Glomark Delkanda","lat":6.68033,"lng":79.98645},
    {"name":"Glomark Kottawa","lat":6.8382,"lng":79.9588},
    {"name":"Glomark Kurunegala","lat":7.4863,"lng":80.3647},
    {"name":"Glomark Nawala","lat":6.8826,"lng":79.8863},
    {"name":"Glomark Mount Lavinia","lat":6.8389,"lng":79.8636},
    {"name":"Glomark Malabe","lat":6.9060,"lng":79.9723},
    {"name":"Glomark CR&FC","lat":6.9069,"lng":79.8690},
    {"name":"Glomark Negombo","lat":7.2083,"lng":79.8358},
    {"name":"Glomark Thalawathugoda","lat":6.8730,"lng":79.9350},
    {"name":"Glomark Kandana","lat":7.0480,"lng":79.8930},
    {"name":"Glomark Kandy Odel Mall","lat":7.2906,"lng":80.6337},
    {"name":"Glomark Horton Place","lat":6.9122,"lng":79.8688},
    {"name":"Glomark Wattala","lat":7.0015,"lng":79.8917},
    {"name":"Glomark Rajagiriya","lat":6.9147,"lng":79.8850},
    {"name":"Glomark Colombo Central","lat":6.9140,"lng":79.8500}
]

def clear_locations_table():
    print("🧹 Wiping old location data...")
    # Using .gt("id", 0) to bypass Supabase delete protection
    supabase.table("store_locations").delete().gt("id", 0).execute()

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"⚠️ Warning: {filename} not found.")
    return []

def run_upload():
    # --- UPDATED PATHS ---
    # We use '../' to go up from 'supabase/' and then into 'data/geocoded/'
    keells_path = '../data/geocoded/geocoded_keells.json'
    cargills_path = '../data/geocoded/geocoded_cargills.json'
    
    keells_data = load_json(keells_path)
    cargills_data = load_json(cargills_path)
    
    # Normalize Glomark to match the table schema
    glomark_normalized = []
    for item in glomark_raw:
        glomark_normalized.append({
            "store_chain": "Glomark",
            "branch_name": item["name"],
            "latitude": item["lat"],
            "longitude": item["lng"],
            "address": "Contact branch for details"
        })

    # Combine all into one massive list
    final_list = keells_data + cargills_data + glomark_normalized
    
    print(f"📊 Total stores found to upload: {len(final_list)}")
    
    # Clear and Upload
    clear_locations_table()
    
    # Batch upload (50 at a time)
    batch_size = 50
    for i in range(0, len(final_list), batch_size):
        batch = final_list[i:i + batch_size]
        try:
            supabase.table("store_locations").insert(batch).execute()
            print(f"✅ Uploaded stores {i} to {i + len(batch)}")
        except Exception as e:
            print(f"❌ Error uploading batch starting at {i}: {e}")

if __name__ == "__main__":
    run_upload()
    print("\n🏁 DONE! All Keells, Cargills, and Glomark locations are in Supabase.")