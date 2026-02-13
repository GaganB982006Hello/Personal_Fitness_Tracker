import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

class DBManager:
    def __init__(self, db_path='fitness_users.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )
            ''')
            # Create default admin if not exists
            new_admin_username = 'gaganb982006@gmail.com'
            admin_exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (new_admin_username,)).fetchone()
            if not admin_exists:
                # Storing plain text password as requested by user
                conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                            (new_admin_username, '123456789', 'admin'))
            conn.commit()

    def create_user(self, username, password):
        try:
            # Storing plain text password as requested by user
            with self.get_connection() as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                            (username, password))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        with self.get_connection() as conn:
            user = conn.execute("SELECT id, username, password, role FROM users WHERE username = ?", 
                               (username,)).fetchone()
            # String comparison for plain text passwords
            if user and user[2] == password:
                return {'id': user[0], 'username': user[1], 'role': user[3]}
        return None

    def get_all_users(self):
        with self.get_connection() as conn:
            users = conn.execute("SELECT id, username, role, password FROM users").fetchall()
            return [{'id': u[0], 'username': u[1], 'role': u[2], 'password': u[3]} for u in users]

    def delete_user(self, user_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
