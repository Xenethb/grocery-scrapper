import json
from rapidfuzz import process, fuzz

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load your three datasets
glomark_data = load_json('glomark_master_data.json')
keells_data = load_json('keells_master_data.json')
cargills_data = load_json('cargills_master_data.json')

master_comparison = []

def find_match(name, choices, threshold=85):
    """Returns the best match from choices if it's above the threshold."""
    match = process.extractOne(name, choices, scorer=fuzz.token_set_ratio)
    if match and match[1] >= threshold:
        return match[0] # Return the matched name
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

# Match Keells into the Master
keells_names = [item['product_name'] for item in keells_data]
for k_item in keells_data:
    match = find_match(k_item['product_name'], all_names)
    if match:
        # Find the index in master and update
        for m_item in master_comparison:
            if m_item['name'] == match:
                m_item['keells_price'] = k_item['price']
    else:
        # No match found, add as a new item
        master_comparison.append({
            "name": k_item['product_name'],
            "glomark_price": None,
            "keells_price": k_item['price'],
            "cargills_price": None
        })
        all_names.append(k_item['product_name'])

# Match Cargills into the Master
cargills_names = [item['product_name'] for item in cargills_data]
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

with open('master_comparison.json', 'w', encoding='utf-8') as f:
    json.dump(master_comparison, f, indent=4)

print(f"Merged! Total unique products across 3 stores: {len(master_comparison)}")