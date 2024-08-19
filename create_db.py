import sqlite3

def create_database():
    print("Connecting to database...")
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    print("Creating table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Table created successfully.")

if __name__ == '__main__':
    create_database()
    print("Database and table created successfully.")
