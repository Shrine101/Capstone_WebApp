import sqlite3
import shutil
from datetime import datetime
import os

def backup_database(db_path):
    """Create a backup of the database before modifications"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"Backup created at: {backup_path}")
    return backup_path

def add_score_before_columns(db_path):
    """Add score_before_throw columns to GameRounds table"""
    # Create backup first
    backup_path = backup_database(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(GameRounds)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add columns if they don't exist
        new_columns = [
            'score_before_throw1',
            'score_before_throw2',
            'score_before_throw3'
        ]
        
        for column in new_columns:
            if column not in columns:
                print(f"Adding {column} column...")
                cursor.execute(f'''
                    ALTER TABLE GameRounds
                    ADD COLUMN {column} INTEGER DEFAULT NULL
                ''')
                print(f"Column {column} added successfully")
            else:
                print(f"Column {column} already exists")
        
        conn.commit()
        print("Database modification completed successfully")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        print(f"Restoring from backup...")
        conn.close()
        shutil.copy2(backup_path, db_path)
        print("Database restored from backup")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    db_path = "dartboard.db"
    if os.path.exists(db_path):
        success = add_score_before_columns(db_path)
        if success:
            print("Migration completed successfully")
            print("\nNext steps:")
            print("1. Update handle_throw_dart() to store scores before each throw")
            print("2. Modify handle_override_throw() to use the correct score_before_throw value")
        else:
            print("Migration failed, database restored from backup")
    else:
        print(f"Database file not found at: {db_path}")
