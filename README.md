# 🧪 Lab Inventory Management System - Core

This directory contains the core application files for the Lab Inventory Management System.

## 🚀 Key Modules

### 1. 🔐 User Authentication
- **Secure Access**: Role-based access control (Admin/Staff).
- **Session Management**: Secure login and logout functionality.

### 2. 🧪 Chemical Inventory
- **Tracking**: Manage chemicals with CAS numbers and formulas.
- **Inventory**: Real-time tracking of quantities and storage locations.
- **Safety**: Monitor expiry dates and safety compliance.

### 3. ⚙️ Equipment Management
- **Asset Tracking**: Register hardware with model and serial numbers.
- **Maintenance**: Automated monitoring of maintenance schedules.
- **Status**: Live status indicators (Working, Broken, etc.).

### 4. 📅 Resource Management
- **Laboratory Booking**: Schedule time slots for shared laboratory assets.
- **Conflict Prevention**: Centralized booking registry.

### 5. 🛒 Purchase Orders
- **Procurement**: Management of stock procurement and order history.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Database**: MySQL
- **Dependencies**: Flask, mysql-connector-python, Werkzeug

## ⚙️ Quick Start

### 1. Database Initialization
1. Create a MySQL database named `lab_inventory_db`.
2. Run `schema.sql` and `purchase_orders.sql` in your database.

### 2. Configuration
Update `db_config` in `app.py` and `init_users.py`:
```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',
    'database': 'lab_inventory_db'
}
```

### 3. Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create admin user
python init_users.py
```

### 4. Execution
```bash
python app.py
```

Access the system at `http://127.0.0.1:5000`.

### 🔑 Demo Credentials
- **Username**: `admin`
- **Password**: `password123`
