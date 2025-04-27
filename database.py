import sqlite3
from werkzeug.security import generate_password_hash
import json

def init_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS health_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            form_data TEXT NOT NULL,
            recommended_plans TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_data TEXT NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_medical_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            condition_name TEXT NOT NULL,
            diagnosis_date DATE,
            current_status TEXT,
            medications TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            profile_id INTEGER,
            rating INTEGER,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (profile_id) REFERENCES health_profiles (id)
        )
    ''')

    sample_users = [
        ('demo_user', generate_password_hash('demo123'), 'demo@example.com'),
        ('test_user', generate_password_hash('test123'), 'test@example.com')
    ]

    for user in sample_users:
        try:
            c.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', user)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_sample_medical_conditions(user_id):
    conn = get_db_connection()
    c = conn.cursor()

    sample_conditions = [
        ('Hypertension', '2023-01-15', 'Controlled', 'Amlodipine 5mg'),
        ('Type 2 Diabetes', '2022-06-20', 'Managed', 'Metformin 1000mg'),
        ('Asthma', '2021-03-10', 'Mild', 'Albuterol inhaler')
    ]

    for condition in sample_conditions:
        c.execute('''
            INSERT INTO user_medical_history 
            (user_id, condition_name, diagnosis_date, current_status, medications)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, *condition))

    conn.commit()
    conn.close()

def clear_database():
    """Function to clear all data from the database (useful for testing)"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    tables = [
        'feedback',
        'user_medical_history',
        'saved_plans',
        'health_profiles',
        'users'
    ]

    for table in tables:
        c.execute(f'DROP TABLE IF EXISTS {table}')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_database()
    conn = get_db_connection()
    demo_user = conn.execute('SELECT id FROM users WHERE username = ?', ('demo_user',)).fetchone()
    if demo_user:
        add_sample_medical_conditions(demo_user['id'])
    conn.close()

    print("Database initialized successfully!")