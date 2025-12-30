# Lab Inventory Management System

A simplified web-based management system for tracking chemical inventory and laboratory equipment.

## 🚀 Key Modules

### 1. Chemical Inventory
- **Tracking**: Manage chemicals with name, CAS number, and formula.
- **Inventory**: Track quantities, units, and storage locations.
- **Safety**: Store expiry dates and safety notes.

### 2. Equipment Management
- **Asset Tracking**: Register hardware with model/serial numbers.
- **Maintenance**: Monitor maintenance schedules and history.
- **Status**: Track if equipment is Working, Broken, or in Maintenance.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5)
- **Database**: MySQL

## ⚙️ Quick Start

1. **Database**: Run `schema.sql` in your MySQL instance.
2. **Dependencies**: `pip install flask mysql-connector-python`
3. **Config**: Update `db_config` in `app.py` with your credentials.
4. **Run**: `python app.py`

Access the system at `http://127.0.0.1:5000`.
