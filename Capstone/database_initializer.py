import sqlite3

#Connect to the database (we use this to create the database, since it does not exist yet)
connection = sqlite3.connect("dartboard.db")
cursor = connection.cursor()

#Create Players table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT
)
''')

#Create Games table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES Players (id)
)
''')


#Save changes and close the connection
connection.commit()
connection.close()
print("Database and tables created successfully.")
