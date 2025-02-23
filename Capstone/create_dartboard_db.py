import sqlite3
from datetime import datetime

def create_dartboard_db():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('simple_dartboard.db')
    cursor = conn.cursor()

    # Create Games table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_name TEXT NOT NULL,
        start_score INTEGER DEFAULT 501,
        current_player_id INTEGER,
        game_status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (current_player_id) REFERENCES players (player_id)
    )
    ''')

    # Create Players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        player_name TEXT NOT NULL,
        current_score INTEGER,
        player_order INTEGER,
        FOREIGN KEY (game_id) REFERENCES games (game_id)
    )
    ''')

    # Create Rounds table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rounds (
        round_id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        player_id INTEGER,
        round_number INTEGER,
        first_throw INTEGER,
        second_throw INTEGER,
        third_throw INTEGER,
        remaining_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games (game_id),
        FOREIGN KEY (player_id) REFERENCES players (player_id)
    )
    ''')

    # Create some sample data
    def insert_sample_game():
        # Insert a new game
        cursor.execute('''
        INSERT INTO games (game_name, start_score, game_status)
        VALUES (?, ?, ?)
        ''', ('Friday Night 501', 501, 'active'))
        game_id = cursor.lastrowid

        # Insert players
        players = [
            ('John', 501, 1),
            ('Sarah', 501, 2),
            ('Mike', 501, 3)
        ]
        
        for player_name, start_score, player_order in players:
            cursor.execute('''
            INSERT INTO players (game_id, player_name, current_score, player_order)
            VALUES (?, ?, ?, ?)
            ''', (game_id, player_name, start_score, player_order))
            player_id = cursor.lastrowid

            # Insert first round for each player
            if player_order == 1:
                cursor.execute('''
                INSERT INTO rounds (game_id, player_id, round_number, first_throw, 
                                  second_throw, third_throw, remaining_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (game_id, player_id, 1, 60, 60, 60, 321))

        # Update current player in game
        cursor.execute('''
        UPDATE games 
        SET current_player_id = (
            SELECT player_id FROM players 
            WHERE game_id = ? AND player_order = 1
        )
        WHERE game_id = ?
        ''', (game_id, game_id))

    # Insert sample data
    insert_sample_game()

    # Commit changes and close connection
    conn.commit()
    conn.close()

def display_db_contents():
    """Helper function to display the contents of the database"""
    conn = sqlite3.connect('simple_dartboard.db')
    cursor = conn.cursor()

    print("\nGames:")
    cursor.execute("SELECT * FROM games")
    print(cursor.fetchall())

    print("\nPlayers:")
    cursor.execute("SELECT * FROM players")
    print(cursor.fetchall())

    print("\nRounds:")
    cursor.execute("SELECT * FROM rounds")
    print(cursor.fetchall())

    conn.close()

if __name__ == "__main__":
    create_dartboard_db()
    display_db_contents()