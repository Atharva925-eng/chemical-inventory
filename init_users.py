import mysql.connector
from werkzeug.security import generate_password_hash
import sys
import os

# Add parent directory to path to import db_config if needed, 
# but we'll just copy it for simplicity in this standalone script
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Athu@123',
    'database': 'lab_inventory_db'
}

def init_users():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                role ENUM('admin', 'staff') DEFAULT 'staff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create a default admin user if not exists
        username = 'admin'
        password = 'password123'
        full_name = 'Lab Administrator'
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if not cursor.fetchone():
            hashed_pw = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (%s, %s, %s, %s)",
                         (username, hashed_pw, full_name, 'admin'))
            conn.commit()
            print(f"User '{username}' created with password '{password}'")
        else:
            print(f"User '{username}' already exists")

        cursor.close()
        conn.close()
        print("Database initialization complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_users()
