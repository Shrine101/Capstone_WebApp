import sqlite3
from sqlite3 import Error

def modify_database():
    try:
        # Connect to database
        conn = sqlite3.connect('dartboard.db')
        cursor = conn.cursor()
        
        # Add new columns to Games table
        modify_columns = [
            "ALTER TABLE Games ADD COLUMN game_type INTEGER NOT NULL DEFAULT 501;",
            "ALTER TABLE Games ADD COLUMN double_out_required BOOLEAN NOT NULL DEFAULT 0;",
            "ALTER TABLE Games ADD COLUMN game_status TEXT DEFAULT 'in_progress';",
            "ALTER TABLE Games ADD COLUMN current_score INTEGER;"
        ]
        
        # Execute each column addition separately (SQLite limitation)
        for command in modify_columns:
            try:
                cursor.execute(command)
                print(f"Successfully executed: {command}")
            except Error as e:
                if 'duplicate column name' in str(e):
                    print(f"Column already exists, skipping: {command}")
                else:
                    print(f"Error executing {command}: {e}")
        
        # Create GameThrows table
        create_throws_table = """
        CREATE TABLE IF NOT EXISTS GameThrows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            throw_number INTEGER NOT NULL,
            score INTEGER NOT NULL,
            multiplier INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES Games (id)
        );
        """
        
        cursor.execute(create_throws_table)
        print("GameThrows table created or already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\nVerifying database structure:")
        
        # Check Games table structure
        cursor.execute("PRAGMA table_info(Games);")
        print("\nGames table columns:")
        for column in cursor.fetchall():
            print(column)
            
        # Check GameThrows table structure
        cursor.execute("PRAGMA table_info(GameThrows);")
        print("\nGameThrows table columns:")
        for column in cursor.fetchall():
            print(column)
            
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed")

if __name__ == "__main__":
    print("Starting database modification...")
    modify_database()
