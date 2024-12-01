def initialize_db(self):
    # Create the `users` table
    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # default admin credentials
    self.cursor.execute('''
        INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
    ''', ("admin", "password"))

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount_paid REAL DEFAULT 0,
            change REAL DEFAULT 0
        )
    ''')

    self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id)
        )
    ''')

    # Commit changes
    self.conn.commit()