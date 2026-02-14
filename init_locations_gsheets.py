from db_sheets import db

def add_default_locations():
    print("Adding default storage locations...")
    
    # Check if locations already exist
    existing = db.select_all('locations')
    if existing:
        print("Locations sheet is not empty. Skipping initialization.")
        return

    default_locs = [
        {'name': 'Flammables Cabinet', 'room_number': '101'},
        {'name': 'Refrigerator A', 'room_number': '102'},
        {'name': 'General Shelf 3', 'room_number': '101'},
        {'name': 'Chemical Storage Room', 'room_number': 'Basement'}
    ]

    try:
        for loc in default_locs:
            loc_id = db.insert('locations', loc, id_prefix='LOC')
            print(f"Added: {loc['name']} (ID: {loc_id})")
        print("\nDefault locations added successfully!")
    except Exception as e:
        print(f"Error adding locations: {e}")

if __name__ == "__main__":
    add_default_locations()
