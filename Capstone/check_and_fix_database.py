import sqlite3

def check_database():
    try:
        with sqlite3.connect('dartboard.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Current tables in database:", tables)
            
            # Check GameRounds table specifically
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='GameRounds';
            """)
            if cursor.fetchone() is None:
                print("GameRounds table doesn't exist, creating it now...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS GameRounds (
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
                    round_total INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games (id),
                    FOREIGN KEY (player_id) REFERENCES Players (id)
                );
                """)
                
                # Create index
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_rounds 
                    ON GameRounds(game_id, player_id, round_number);
                """)
                conn.commit()
                print("GameRounds table created successfully")
            else:
                print("GameRounds table exists")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_database()
