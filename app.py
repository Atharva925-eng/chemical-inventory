from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'super-secret-lab-key-123' # Static secret key for stable sessions

# --- DATABASE CONFIGURATION ---
# UPDATE 'password' with your real MySQL password!
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Athu@123',  # <--- DID YOU CHANGE THIS?
    'database': 'lab_inventory_db'
}


def get_db_connection():
    """Establishes connection to MySQL"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

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
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error', 'danger')
            return render_template('login.html')
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            if check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please check your credentials and try again.', 'danger')
        else:
            flash(f'Invalid username or password. Please check your credentials and try again.', 'danger')
            
    return render_template('login.html')

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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT c.*, l.name as location_name 
        FROM chemicals c 
        LEFT JOIN locations l ON c.location_id = l.id
        ORDER BY c.created_at DESC
    """
    cursor.execute(query)
    chemicals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(chemicals)

# 2. Get Single Chemical
@app.route('/api/chemicals/<int:id>', methods=['GET'])
def get_chemical(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chemicals WHERE id = %s", (id,))
    chemical = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if chemical:
        return jsonify(chemical)
    return jsonify({'error': 'Chemical not found'}), 404

# 3. Add or Update Chemical
@app.route('/api/chemicals', methods=['POST'])
def save_chemical():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    expiry = data.get('expiry_date')
    if not expiry or expiry == '':
        expiry = None
    
    loc_id = data.get('location_id')
    if not loc_id or loc_id == '':
        loc_id = None

    try:
        if data.get('id'):
            query = """
                UPDATE chemicals 
                SET name=%s, cas_number=%s, quantity=%s, unit=%s, 
                    location_id=%s, expiry_date=%s, safety_notes=%s 
                WHERE id=%s
            """
            vals = (data['name'], data['cas_number'], data['quantity'], data['unit'], 
                    loc_id, expiry, data['safety_notes'], data['id'])
            cursor.execute(query, vals)
        else:
            query = """
                INSERT INTO chemicals (name, cas_number, quantity, unit, location_id, expiry_date, safety_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            vals = (data['name'], data['cas_number'], data['quantity'], data['unit'], 
                    loc_id, expiry, data['safety_notes'])
            cursor.execute(query, vals)

        conn.commit()
        return jsonify({'message': 'Success'}), 201

    except Exception as e:
        print(f"ERROR SAVING CHEMICAL: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# 4. Delete Chemical
@app.route('/api/chemicals/<int:id>', methods=['DELETE'])
def delete_chemical(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chemicals WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

# --- EQUIPMENT API ---

# 1. Get All Equipments
@app.route('/api/equipments', methods=['GET'])
def get_equipments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT e.*, l.name as location_name 
        FROM equipments e 
        LEFT JOIN locations l ON e.location_id = l.id
        ORDER BY e.created_at DESC
    """
    cursor.execute(query)
    equipments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(equipments)

# 2. Get Single Equipment
@app.route('/api/equipments/<int:id>', methods=['GET'])
def get_equipment_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipments WHERE id = %s", (id,))
    equip = cursor.fetchone()
    cursor.close()
    conn.close()
    if equip:
        return jsonify(equip)
    return jsonify({'error': 'Equipment not found'}), 404

# 3. Add or Update Equipment
@app.route('/api/equipments', methods=['POST'])
def save_equipment():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Dates
    p_date = data.get('purchase_date') or None
    lm_date = data.get('last_maintenance_date') or None
    nm_date = data.get('next_maintenance_date') or None
    loc_id = data.get('location_id') or None

    try:
        if data.get('id'):
            # UPDATE
            query = """
                UPDATE equipments 
                SET name=%s, model_number=%s, serial_number=%s, manufacturer=%s, 
                    quantity=%s, location_id=%s, purchase_date=%s, 
                    last_maintenance_date=%s, next_maintenance_date=%s, 
                    status=%s, description=%s 
                WHERE id=%s
            """
            vals = (data['name'], data['model_number'], data['serial_number'], data['manufacturer'],
                    data['quantity'], loc_id, p_date, lm_date, nm_date, 
                    data['status'], data['description'], data['id'])
            cursor.execute(query, vals)
        else:
            # INSERT
            query = """
                INSERT INTO equipments (name, model_number, serial_number, manufacturer, 
                                     quantity, location_id, purchase_date, 
                                     last_maintenance_date, next_maintenance_date, 
                                     status, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            vals = (data['name'], data['model_number'], data['serial_number'], data['manufacturer'],
                    data['quantity'], loc_id, p_date, lm_date, nm_date, 
                    data['status'], data['description'])
            cursor.execute(query, vals)

        conn.commit()
        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        print(f"ERROR SAVING EQUIPMENT: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 4. Delete Equipment
@app.route('/api/equipments/<int:id>', methods=['DELETE'])
def delete_equipment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM equipments WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

# --- COMMON API ---

@app.route('/api/locations', methods=['GET'])
def get_locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(locations)

# --- BOOKINGS API ---

# 1. Get All Bookings
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bookings ORDER BY booking_date DESC")
    bookings = cursor.fetchall()
    
    # Format date for JSON
    for b in bookings:
        if b['booking_date']:
            b['booking_date'] = b['booking_date'].isoformat()
            
    cursor.close()
    conn.close()
    return jsonify(bookings)

# 2. Add New Booking
@app.route('/api/bookings', methods=['POST'])
def save_booking():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            INSERT INTO bookings (type, resource_name, researcher_name, booking_date)
            VALUES (%s, %s, %s, %s)
        """
        vals = (data['type'], data['resourceName'], data['researcherName'], data['date'])
        cursor.execute(query, vals)
        conn.commit()
        return jsonify({'message': 'Success', 'id': cursor.lastrowid}), 201
    except Exception as e:
        print(f"ERROR SAVING BOOKING: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 3. Delete Booking
@app.route('/api/bookings/<int:id>', methods=['DELETE'])
def delete_booking_api(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

# --- PURCHASE ORDERS API ---

@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM purchase_orders ORDER BY order_date DESC")
        orders = cursor.fetchall()
        # Format dates for JSON
        for o in orders:
            if o['order_date']:
                o['order_date'] = o['order_date'].strftime('%Y-%m-%d')
        return jsonify(orders)
    except Exception as e:
        print(f"ERROR FETCHING ORDERS: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/orders', methods=['POST'])
@login_required
def save_order():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO purchase_orders (po_number, supplier, order_date, items, total_cost, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        vals = (data['po_number'], data['supplier'], data['order_date'], 
                data['items'], data['total_cost'], data['status'])
        cursor.execute(query, vals)
        conn.commit()
        return jsonify({'message': 'Success', 'id': cursor.lastrowid}), 201
    except Exception as e:
        print(f"ERROR SAVING ORDER: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
