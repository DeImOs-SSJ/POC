import sqlite3

def create_database():
    print("Connecting to database...")
    conn = sqlite3.connect('app.db')  # Renamed to app.db for clarity
    c = conn.cursor()
    print("Creating tables...")

    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            company_email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully.")

if __name__ == '__main__':
    create_database()
    print("Database and tables created successfully.")
