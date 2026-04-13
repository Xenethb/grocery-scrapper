import json
import os
from rapidfuzz import process, fuzz

def load_json(filename):
    # We added encoding and a check to make sure the file exists
    if not os.path.exists(filename):
        print(f"❌ Error: {filename} not found!")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- UPDATED PATHS ---
# We use '../' to go out of the 'utils' folder and into 'data/raw'
glomark_data = load_json('../data/raw/glomark_master_data.json')
keells_data = load_json('../data/raw/keells_master_data.json')
cargills_data = load_json('../data/raw/cargills_master_data.json')

master_comparison = []

def find_match(name, choices, threshold=85):
    match = process.extractOne(name, choices, scorer=fuzz.token_set_ratio)
    if match and match[1] >= threshold:
        return match[0]
    return None

# Start with Glomark as the base
all_names = [item['product_name'] for item in glomark_data]
for item in glomark_data:
    master_comparison.append({
        "name": item['product_name'],
        "glomark_price": item['price'],
        "keells_price": None,
        "cargills_price": None
    })

# Match Keells
for k_item in keells_data:
    match = find_match(k_item['product_name'], all_names)
    if match:
        for m_item in master_comparison:
            if m_item['name'] == match:
                m_item['keells_price'] = k_item['price']
    else:
        master_comparison.append({
            "name": k_item['product_name'],
            "glomark_price": None,
            "keells_price": k_item['price'],
            "cargills_price": None
        })
        all_names.append(k_item['product_name'])

# Match Cargills
for c_item in cargills_data:
    match = find_match(c_item['product_name'], all_names)
    if match:
        for m_item in master_comparison:
            if m_item['name'] == match:
                m_item['cargills_price'] = c_item['price']
    else:
        master_comparison.append({
            "name": c_item['product_name'],
            "glomark_price": None,
            "keells_price": None,
            "cargills_price": c_item['price']
        })
        all_names.append(c_item['product_name'])

# --- UPDATED SAVE PATH ---
# Save the final file in the main 'data/' folder
output_path = '../data/master_comparison.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(master_comparison, f, indent=4)

print(f"✅ Merged! Total unique products saved to {output_path}: {len(master_comparison)}")