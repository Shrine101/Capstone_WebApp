import sqlite3
from contextlib import contextmanager
import os
from datetime import datetime

DB_FILE = 'dartboard.db'
BACKUP_FILE = f'dartboard_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def backup_database():
    """Create a backup of the current database"""
    import shutil
    if os.path.exists(DB_FILE):
        shutil.copy2(DB_FILE, BACKUP_FILE)
        print(f"Created backup at {BACKUP_FILE}")

def update_schema():
    print("Starting database schema update...")
    
    try:
        backup_database()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if is_bust column exists
            cursor.execute('''
                SELECT COUNT(*) as count
                FROM pragma_table_info('GameRounds')
                WHERE name = 'is_bust'
            ''')
            
            if cursor.fetchone()['count'] == 0:
                print("Adding is_bust column to GameRounds table...")
                cursor.execute('''
                    ALTER TABLE GameRounds
                    ADD COLUMN is_bust BOOLEAN DEFAULT 0
                ''')
                print("Column added successfully")
            else:
                print("is_bust column already exists")
            
            conn.commit()
            print("Schema update completed successfully!")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=== Database Schema Update Script ===")
    if update_schema():
        print("Schema update completed successfully!")
        print(f"A backup of your original database has been saved as {BACKUP_FILE}")
    else:
        print("Schema update failed!")
