import sqlite3
import randfacts

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create users table with role column
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'user')''')

# create a default user
c.execute("INSERT OR IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
          ('user', 'user@example.com', 'user_password', 'user'))

# Create a default admin user
c.execute("INSERT OR IGNORE INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
          ('admin', 'admin@example.com', 'admin_password', 'admin'))

print("Database, users table, and default admin user created successfully.")

c.execute('''CREATE TABLE IF NOT EXISTS facts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              content TEXT NOT NULL)''')



for i in range(100):
    x = randfacts.get_fact()

    c.execute("INSERT OR IGNORE INTO facts (content) VALUES (?)", (x,))

conn.commit()
conn.close()

print("Sample facts created successfully.")
