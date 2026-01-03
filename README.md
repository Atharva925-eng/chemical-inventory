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
- **Database**: PostgreSQL

## ⚙️ Quick Start

### Prerequisites
- Python 3.x
- PostgreSQL installed and running (default user `postgres` or system user).

### Setup

1. **Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install flask psycopg2-binary
   ```

2. **Database Setup**:
   Run the setup script to create the database and tables (uses your system username by default on macOS):
   ```bash
   python setup_postgres.py
   ```
   *Note: If connection fails, check `setup_postgres.py` and `app.py` to match your local PostgreSQL credentials.*

3. **Run Application**:
   ```bash
   python app.py
   ```

Access the system at `http://127.0.0.1:5000`.
