import gspread
from google.oauth2.service_account import Credentials

# Scopes for Google Sheets and Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def init_database(spreadsheet_name="lab_inventory_db", credentials_file="credentials.json"):
    try:
        creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Create or open spreadsheet
        try:
            sh = client.open(spreadsheet_name)
            print(f"Opening existing spreadsheet: {spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            sh = client.create(spreadsheet_name)
            print(f"Created new spreadsheet: {spreadsheet_name}")
            # Share with your email if needed: sh.share('your-email@gmail.com', perm_type='user', role='writer')

        # Define headers for each sheet
        sheets_config = {
            "users": ["id", "username", "password_hash", "full_name", "role", "created_at"],
            "chemicals": ["id", "cas_number", "name", "formula", "quantity", "unit", "location_id", "expiry_date", "safety_notes", "created_at", "updated_at"],
            "equipment": ["id", "name", "model_number", "serial_number", "manufacturer", "quantity", "location_id", "purchase_date", "last_maint", "next_maint", "status", "description", "created_at", "updated_at"],
            "bookings": ["id", "type", "resource_name", "researcher", "booking_date", "created_at"],
            "orders": ["id", "po_number", "supplier", "order_date", "items", "total_cost", "status", "created_at", "updated_at"],
            "locations": ["id", "name", "room_number"]
        }

        for sheet_name, headers in sheets_config.items():
            try:
                worksheet = sh.worksheet(sheet_name)
                print(f"Sheet '{sheet_name}' already exists.")
            except gspread.WorksheetNotFound:
                worksheet = sh.add_worksheet(title=sheet_name, rows="100", cols=len(headers))
                worksheet.update('A1', [headers])
                print(f"Created sheet: {sheet_name}")

        # Remove default 'Sheet1' if it exists and isn't used
        try:
            default_sheet = sh.worksheet("Sheet1")
            sh.del_worksheet(default_sheet)
        except:
            pass

        print("\nInitialization Complete!")
        print(f"Spreadsheet URL: {sh.url}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure 'credentials.json' is in the project root and the Service Account has permissions.")

if __name__ == "__main__":
    init_database()
