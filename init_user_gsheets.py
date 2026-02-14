from werkzeug.security import generate_password_hash
from db_sheets import db

def add_default_user():
    print("Adding default administrative user...")
    
    # Check if a user already exists
    existing_user = db.select_all('users')
    if existing_user:
        print("User sheet is not empty. Skipping default user creation.")
        return

    # Default admin credentials
    username = "admin"
    password = "admin_password" # Change this after first login!
    full_name = "Lab Administrator"
    role = "admin"

    user_data = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "full_name": full_name,
        "role": role
    }

    try:
        user_id = db.insert('users', user_data, id_prefix='USR')
        print(f"Success! Admin user created.")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"User ID: {user_id}")
    except Exception as e:
        print(f"Error adding user: {e}")

if __name__ == "__main__":
    add_default_user()
