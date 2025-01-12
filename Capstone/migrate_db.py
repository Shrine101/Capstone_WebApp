import sqlite3
import os
from contextlib import contextmanager
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

def get_current_schema(conn):
    """Get the current table structure excluding system tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT IN ('sqlite_sequence')")
    return [row[0] for row in cursor.fetchall()]

def backup_players_data(conn):
    """Backup existing players data"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Players')
    return [dict(row) for row in cursor.fetchall()]

def drop_tables(conn, tables):
    """Drop specified tables"""
    cursor = conn.cursor()
    # Delete all rows from sqlite_sequence to reset auto-increment counters
    cursor.execute('DELETE FROM sqlite_sequence')
    
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')

def create_new_schema(conn):
    """Create the new database schema"""
    cursor = conn.cursor()
    
    # Preserve Players table structure
    cursor.execute('''
    CREATE TABLE Players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT
    )
    ''')

    # GameRooms table for multiplayer support
    cursor.execute('''
    CREATE TABLE GameRooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        room_status TEXT DEFAULT 'waiting',
        game_type INTEGER NOT NULL,
        double_out_required BOOLEAN DEFAULT 0,
        is_private BOOLEAN DEFAULT 0,
        room_password TEXT,
        max_players INTEGER DEFAULT 10,
        current_players INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES Players (id),
        CHECK (room_status IN ('waiting', 'in_progress', 'completed', 'abandoned')),
        CHECK (game_type IN (301, 501)),
        CHECK (current_players <= max_players)
    )
    ''')

    # Games table (modified for rooms)
    cursor.execute('''
    CREATE TABLE Games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        game_status TEXT DEFAULT 'in_progress',
        current_player_position INTEGER DEFAULT 0,
        FOREIGN KEY (room_id) REFERENCES GameRooms (id),
        CHECK (game_status IN ('in_progress', 'completed', 'abandoned'))
    )
    ''')

    # GamePlayers junction table
    cursor.execute('''
    CREATE TABLE GamePlayers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        player_id INTEGER NOT NULL,
        player_position INTEGER NOT NULL,
        current_score INTEGER NOT NULL,
        player_status TEXT DEFAULT 'active',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES Games (id),
        FOREIGN KEY (player_id) REFERENCES Players (id),
        CHECK (player_status IN ('active', 'disconnected', 'finished')),
        UNIQUE (game_id, player_position)
    )
    ''')

    # GameRounds table (preserved structure with room support)
    cursor.execute('''
    CREATE TABLE GameRounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        player_id INTEGER NOT NULL,
        round_number INTEGER NOT NULL,
        throw1_score INTEGER,
        throw1_multiplier INTEGER,
        throw2_score INTEGER,
        throw2_multiplier INTEGER,
        throw3_score INTEGER,
        throw3_multiplier INTEGER,
        round_total INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES Games (id),
        FOREIGN KEY (player_id) REFERENCES Players (id)
    )
    ''')

    # Create necessary indexes
    cursor.execute('CREATE INDEX idx_gamerooms_status ON GameRooms (room_status)')
    cursor.execute('CREATE INDEX idx_games_room ON Games (room_id)')
    cursor.execute('CREATE INDEX idx_gameplayers_game ON GamePlayers (game_id)')
    cursor.execute('CREATE INDEX idx_gamerounds_game_player ON GameRounds (game_id, player_id)')

def restore_players_data(conn, players_data):
    """Restore the backed up players data"""
    cursor = conn.cursor()
    for player in players_data:
        cursor.execute('''
        INSERT INTO Players (id, username, password, email)
        VALUES (?, ?, ?, ?)
        ''', (player['id'], player['username'], player['password'], player['email']))

def main():
    print("Starting database migration...")
    
    # Create database backup
    backup_database()
    print("Database backup created")
    
    with get_db_connection() as conn:
        # Get current schema
        current_tables = get_current_schema(conn)
        print(f"Current tables: {', '.join(current_tables)}")
        
        # Backup players data
        players_data = backup_players_data(conn)
        print(f"Backed up {len(players_data)} player records")
        
        # Drop all existing tables
        print("Dropping existing tables...")
        drop_tables(conn, current_tables)
        
        # Create new schema
        print("Creating new schema...")
        create_new_schema(conn)
        
        # Restore players data
        print("Restoring players data...")
        restore_players_data(conn, players_data)
        
    print("Migration completed successfully!")
    print(f"A backup of your original database has been saved as {BACKUP_FILE}")

if __name__ == '__main__':
    main()
