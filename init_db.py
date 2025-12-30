import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Athu@123',
    'database': 'lab_inventory_db'
}

def create_equipment_table():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # SQL for equipment table
        sql = """
        CREATE TABLE IF NOT EXISTS equipments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            model_number VARCHAR(100),
            serial_number VARCHAR(100),
            manufacturer VARCHAR(100),
            quantity INT NOT NULL DEFAULT 1,
            location_id INT,
            purchase_date DATE,
            last_maintenance_date DATE,
            next_maintenance_date DATE,
            status ENUM('Working', 'Maintenance', 'Broken', 'Retired') DEFAULT 'Working',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE SET NULL
        );
        """
        
        print("Checking if 'equipments' table exists...")
        cursor.execute(sql)
        print("Success: 'equipments' table is now ready!")
        
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_equipment_table()
