import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
from google.oauth2.service_account import Credentials

# Scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetsDB:
    def __init__(self, spreadsheet_name="lab_inventory_db", credentials_file="credentials.json"):
        try:
            # Check for Environment Variable first (For Cloud Deployment)
            env_creds = os.environ.get('GOOGLE_SHEETS_CREDS_JSON')
            
            if env_creds:
                # Load from Environment variable string
                creds_dict = json.loads(env_creds)
                creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            elif os.path.exists(credentials_file):
                # Load from local file
                creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
            else:
                raise FileNotFoundError("No credentials found in environment or local file.")

            self.client = gspread.authorize(creds)
            self.sh = self.client.open(spreadsheet_name)
        except Exception as e:
            print(f"SheetsDB Init Error: {e}")
            self.sh = None

    def get_worksheet(self, name):
        if not self.sh: return None
        try:
            return self.sh.worksheet(name)
        except:
            return None

    def _get_all_as_dict(self, worksheet):
        data = worksheet.get_all_records()
        return data

    def _generate_id(self, worksheet, prefix):
        records = worksheet.get_all_records()
        if not records:
            return f"{prefix}-1001"
        
        # Extract numeric parts from IDs like "CHM-1001"
        last_id = records[-1].get('id', '')
        try:
            last_num = int(last_id.split('-')[-1])
            return f"{prefix}-{last_num + 1}"
        except:
            return f"{prefix}-{1000 + len(records) + 1}"

    # --- Generic CRUD ---

    def select_all(self, sheet_name):
        ws = self.get_worksheet(sheet_name)
        if not ws: return []
        return self._get_all_as_dict(ws)

    def select_by_id(self, sheet_name, record_id):
        records = self.select_all(sheet_name)
        for r in records:
            if str(r.get('id')) == str(record_id):
                return r
        return None

    def select_one_by_field(self, sheet_name, field, value):
        records = self.select_all(sheet_name)
        for r in records:
            if str(r.get(field)) == str(value):
                return r
        return None

    def insert(self, sheet_name, data, id_prefix=None):
        ws = self.get_worksheet(sheet_name)
        if not ws: return None
        
        headers = ws.row_values(1)
        
        if id_prefix:
            data['id'] = self._generate_id(ws, id_prefix)
        
        if 'created_at' in headers:
            data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'updated_at' in headers:
            data['updated_at'] = data['created_at']

        # Map data to header order
        row = [data.get(h, "") for h in headers]
        ws.append_row(row)
        return data.get('id')

    def update(self, sheet_name, record_id, data):
        ws = self.get_worksheet(sheet_name)
        if not ws: return False
        
        records = ws.get_all_records()
        headers = ws.row_values(1)
        
        row_idx = -1
        for i, r in enumerate(records):
            if str(r.get('id')) == str(record_id):
                row_idx = i + 2 # 1-indexed + header row
                break
        
        if row_idx == -1: return False

        if 'updated_at' in headers:
            data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update specific columns
        for key, value in data.items():
            if key in headers:
                col_idx = headers.index(key) + 1
                ws.update_cell(row_idx, col_idx, value)
        
        return True

    def delete(self, sheet_name, record_id):
        ws = self.get_worksheet(sheet_name)
        if not ws: return False
        
        records = ws.get_all_records()
        row_idx = -1
        for i, r in enumerate(records):
            if str(r.get('id')) == str(record_id):
                row_idx = i + 2
                break
        
        if row_idx != -1:
            ws.delete_rows(row_idx)
            return True
        return False

# Global instance
db = SheetsDB()
