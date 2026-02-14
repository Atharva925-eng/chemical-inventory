from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
# import mysql.connector
# from mysql.connector import Error
from db_sheets import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import requests

app = Flask(__name__)
app.secret_key = 'super-secret-lab-key-123' # Static secret key for stable sessions

# --- DATABASE CONFIGURATION ---
# Now using Google Sheets via db_sheets.py
# Make sure credentials.json is present in the root folder.

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES: SERVE HTML PAGES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.select_one_by_field('users', 'username', username)
        
        if user:
            if check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')
        else:
            flash(f'Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # Check if user already exists
        existing_user = db.select_one_by_field('users', 'username', username)
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return render_template('register.html')
            
        # Hash password and save user
        user_data = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'role': 'staff' # Default role
        }
        
        try:
            db.insert('users', user_data, id_prefix='USR')
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"ERROR DURING REGISTRATION: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('home.html')

@app.route('/chemicals')
@login_required
def chemicals():
    return render_template('chemicals.html')

@app.route('/equipment')
@login_required
def equipment():
    return render_template('equipment.html')

@app.route('/equipment/form')
@login_required
def item_form():
    return render_template('equipment_form.html')

@app.route('/form.html')
@login_required
def form():
    return render_template('form.html')

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

@app.route('/resource-management')
@login_required
def resource_management():
    return render_template('resource_management.html')

# --- API ENDPOINTS (The "Bridge") ---

# --- CHEMICALS API ---

# 1. Get All Chemicals
@app.route('/api/chemicals', methods=['GET'])
def get_chemicals():
    chemicals = db.select_all('chemicals')
    locations = {str(l['id']): l['name'] for l in db.select_all('locations')}
    
    for c in chemicals:
        # Join location name
        loc_id = str(c.get('location_id', ''))
        c['location_name'] = locations.get(loc_id, 'Unknown')
    
    # Sort by created_at desc (Sheets is usually append-only, so reverse it)
    chemicals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(chemicals)

# 2. Get Single Chemical
@app.route('/api/chemicals/<string:id>', methods=['GET'])
def get_chemical(id):
    chemical = db.select_by_id('chemicals', id)
    if chemical:
        return jsonify(chemical)
    return jsonify({'error': 'Chemical not found'}), 404

# 3. Add or Update Chemical
@app.route('/api/chemicals', methods=['POST'])
def save_chemical():
    data = request.json
    
    try:
        if data.get('id'):
            # UPDATE
            record_id = data['id']
            # Remove id and location_name (if present) from update payload
            update_data = {k: v for k, v in data.items() if k not in ['id', 'location_name']}
            db.update('chemicals', record_id, update_data)
        else:
            # INSERT
            db.insert('chemicals', data, id_prefix='CHM')

        return jsonify({'message': 'Success'}), 201

    except Exception as e:
        print(f"ERROR SAVING CHEMICAL: {e}")
        return jsonify({'error': str(e)}), 500

# 4. Delete Chemical
@app.route('/api/chemicals/<string:id>', methods=['DELETE'])
def delete_chemical(id):
    db.delete('chemicals', id)
    return jsonify({'message': 'Deleted successfully'})

# 5. Chemical Suggestion (PubChem API - No Key Required)
@app.route('/api/chemicals/suggest', methods=['POST'])
@login_required
def suggest_chemical():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Chemical name is required'}), 400

    try:
        # Search for CID (PubChem ID)
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
        search_res = requests.get(search_url, timeout=5)
        if search_res.status_code != 200:
            return jsonify({'error': 'Chemical not found'}), 404
        
        cid = search_res.json()['IdentifierList']['CID'][0]

        # Get Details (Formula, Name, CAS)
        detail_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON"
        detail_res = requests.get(detail_url, timeout=5)
        detail_data = detail_res.json()['PC_Compounds'][0]

        res = {
            'name': name.capitalize(),
            'cas_number': '',
            'formula': '',
            'safety_notes': 'Information fetched from PubChem.',
            'suggested_location': 'General Shelf'
        }

        # Extract Formula and Name
        for prop in detail_data.get('props', []):
            label = prop.get('urn', {}).get('label', '')
            if label == 'Molecular Formula':
                res['formula'] = prop.get('value', {}).get('sval', '')
            if label == 'IUPAC Name' and prop.get('urn', {}).get('name', '') == 'Preferred':
                res['name'] = prop.get('value', {}).get('sval', '')

        # Get Synonyms for CAS
        syn_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        syn_res = requests.get(syn_url, timeout=5)
        if syn_res.status_code == 200:
            synonyms = syn_res.json().get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
            import re
            cas_regex = re.compile(r'^\d{2,7}-\d{2}-\d$')
            for s in synonyms:
                if cas_regex.match(s):
                    res['cas_number'] = s
                    break

        # Suggest Location & Safety
        if res['formula']:
            res['safety_notes'] = f"[Formula: {res['formula']}] "
        
        low_name = res['name'].lower()
        if any(x in low_name for x in ['acetone', 'ethanol', 'methanol', 'ether']):
            res['suggested_location'] = 'Flammables Cabinet'
            res['safety_notes'] += "Flammable. "
        
        return jsonify(res)

    except Exception as e:
        print(f"PUBCHEM ERROR: {e}")
        return jsonify({'error': 'Failed to fetch data from PubChem'}), 500

# --- EQUIPMENT API ---

# 1. Get All Equipments
@app.route('/api/equipments', methods=['GET'])
def get_equipments():
    equipments = db.select_all('equipment')
    locations = {str(l['id']): l['name'] for l in db.select_all('locations')}
    
    for e in equipments:
        loc_id = str(e.get('location_id', ''))
        e['location_name'] = locations.get(loc_id, 'Unknown')
        
    equipments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(equipments)

# 2. Get Single Equipment
@app.route('/api/equipments/<string:id>', methods=['GET'])
def get_equipment_by_id(id):
    equip = db.select_by_id('equipment', id)
    if equip:
        return jsonify(equip)
    return jsonify({'error': 'Equipment not found'}), 404

# 3. Add or Update Equipment
@app.route('/api/equipments', methods=['POST'])
def save_equipment():
    data = request.json
    try:
        if data.get('id'):
            # UPDATE
            record_id = data['id']
            update_data = {k: v for k, v in data.items() if k not in ['id', 'location_name']}
            db.update('equipment', record_id, update_data)
        else:
            # INSERT
            db.insert('equipment', data, id_prefix='EQP')
        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        print(f"ERROR SAVING EQUIPMENT: {e}")
        return jsonify({'error': str(e)}), 500

# 4. Delete Equipment
@app.route('/api/equipments/<string:id>', methods=['DELETE'])
def delete_equipment(id):
    db.delete('equipment', id)
    return jsonify({'message': 'Deleted successfully'})

# --- COMMON API ---

@app.route('/api/locations', methods=['GET'])
def get_locations():
    locations = db.select_all('locations')
    return jsonify(locations)

# --- BOOKINGS API ---

# 1. Get All Bookings
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = db.select_all('bookings')
    bookings.sort(key=lambda x: x.get('booking_date', ''), reverse=True)
    return jsonify(bookings)

# 2. Add New Booking
@app.route('/api/bookings', methods=['POST'])
def save_booking():
    data = request.json
    try:
        # Map frontend keys to Sheet headers if necessary
        # Sheets: ["id", "type", "resource_name", "researcher", "booking_date", "created_at"]
        payload = {
            'type': data.get('type'),
            'resource_name': data.get('resourceName'),
            'researcher': data.get('researcherName'),
            'booking_date': data.get('date')
        }
        new_id = db.insert('bookings', payload, id_prefix='BKG')
        return jsonify({'message': 'Success', 'id': new_id}), 201
    except Exception as e:
        print(f"ERROR SAVING BOOKING: {e}")
        return jsonify({'error': str(e)}), 500

# 3. Delete Booking
@app.route('/api/bookings/<string:id>', methods=['DELETE'])
def delete_booking_api(id):
    db.delete('bookings', id)
    return jsonify({'message': 'Deleted successfully'})

# --- PURCHASE ORDERS API ---

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    try:
        orders = db.select_all('orders')
        orders.sort(key=lambda x: x.get('order_date', ''), reverse=True)
        return jsonify(orders)
    except Exception as e:
        print(f"ERROR FETCHING ORDERS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
@login_required
def save_order():
    data = request.json
    try:
        new_id = db.insert('orders', data, id_prefix='ORD')
        return jsonify({'message': 'Success', 'id': new_id}), 201
    except Exception as e:
        print(f"ERROR SAVING ORDER: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
