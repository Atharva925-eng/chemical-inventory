# 🧪 Lab Inventory Management System

A comprehensive web-based platform designed for modern laboratories to track chemical inventory, manage equipment maintenance, schedule resources, and handle procurement.

## 🚀 Key Modules

### 1. 🔐 User Authentication
- **Secure Access**: Role-based access control (Admin/Staff).
- **Session Management**: Secure login and logout functionality.
- **Account Protection**: Passwords stored using PBKDF2 hashing.

### 2. 🧪 Chemical Inventory
- **Tracking**: Manage chemicals with CAS numbers, formulas, and grades.
- **Inventory**: Real-time tracking of quantities, units, and precise storage locations.
- **Safety**: Monitor expiry dates and safety notes to ensure lab compliance.

### 3. ⚙️ Equipment Management
- **Asset Tracking**: Register hardware with model and serial numbers.
- **Maintenance**: Automated monitoring of maintenance schedules and history.
- **Status Dashboard**: Visual indicators for Working, Broken, or Maintenance status.

### 4. 📅 Resource Management
- **Laboratory Booking**: Schedule time slots for shared lab resources or spaces.
- **Conflict Prevention**: View existing bookings to avoid scheduling overlaps.
- **Unified Interface**: Integrated calendar-style booking system.

### 5. 🛒 Purchase Orders
- **Procurement**: Create and track orders for new stock and maintenance.
- **History**: Maintain a log of all orders with status updates.
- **Financial Tracking**: Monitor estimated costs and vendor information.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Database**: Google Sheets (via Google Sheets API v4)
- **Authentication**: Werkzeug Security (PBKDF2 Hashing)
- **Deployment**: Render ready (Gunicorn)

## 📂 Project Structure
```
minor-lab-management/
├── Lab-inventory/
│   ├── app.py                  # Main Flask application
│   ├── db_sheets.py            # Google Sheets database wrapper
│   ├── init_gsheets.py         # Spreadsheet initialization
│   ├── init_locations_gsheets.py # Storage areas initialization
│   ├── init_user_gsheets.py    # Default admin setup
│   ├── templates/              # HTML templates (Register, Login, etc.)
│   └── static/                 # CSS and JavaScript assets
├── credentials.json            # Google Service Account Key (Git Ignored)
├── methodology.png             # Project workflow diagram
└── README.md                   # Main documentation
```

## ⚙️ Quick Start

### 1. Google Cloud Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Sheets API** and **Google Drive API**.
3. Create a **Service Account** and download the **JSON Key**.
4. Rename it to `credentials.json` and place it in the `Lab-inventory/` folder.

### 2. Install Dependencies
```bash
pip install -r Lab-inventory/requirements.txt
```

### 3. Initialize Database
Run these scripts in order to set up your sheets and initial data:
```bash
# Set up tabs & headers
python Lab-inventory/init_gsheets.py

# Add default storage areas
python Lab-inventory/init_locations_gsheets.py

# Create first admin user
python Lab-inventory/init_user_gsheets.py
```

### 4. Share the Sheet
Open your `lab_inventory_db` sheet in your browser and **Share** it with the `client_email` found in your `credentials.json` (Editor access).

### 5. Launch
```bash
python Lab-inventory/app.py
```

### 🔑 Default Credentials
- **Username**: `admin`
- **Password**: `admin_password` (Change after first login!)
