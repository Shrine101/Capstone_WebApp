from flask import Flask, render_template, Response, jsonify
import sqlite3
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)

DB_FILE = 'simple_dartboard.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_game_data():
    conn = get_db_connection()
    try:
        # Get active game info
        game = conn.execute('''
            SELECT g.*, p.player_name as current_player_name 
            FROM games g
            LEFT JOIN players p ON g.current_player_id = p.player_id
            WHERE g.game_status = 'active'
            ORDER BY g.game_id DESC LIMIT 1
        ''').fetchone()
        
        if not game:
            return None

        # Get players for this game
        players = conn.execute('''
            SELECT p.*, 
                   (SELECT COUNT(*) FROM rounds r WHERE r.player_id = p.player_id) as rounds_played
            FROM players p 
            WHERE p.game_id = ? 
            ORDER BY p.player_order
        ''', [game['game_id']]).fetchall()

        # Get rounds for this game
        rounds = conn.execute('''
            SELECT r.*, p.player_name 
            FROM rounds r
            JOIN players p ON r.player_id = p.player_id
            WHERE r.game_id = ?
            ORDER BY r.round_number, p.player_order
        ''', [game['game_id']]).fetchall()

        return {
            'game': dict(game),
            'players': [dict(player) for player in players],
            'rounds': [dict(round) for round in rounds]
        }
    finally:
        conn.close()

class DatabaseChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = datetime.now().timestamp()
        
    def on_modified(self, event):
        if event.src_path.endswith(DB_FILE):
            self.last_modified = datetime.now().timestamp()

# Set up file watching
observer = Observer()
event_handler = DatabaseChangeHandler()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game-data')
def game_data():
    data = get_game_data()
    if data:
        return jsonify(data)
    return jsonify({'error': 'No active game found'})

@app.route('/stream')
def stream():
    def generate():
        last_check = 0
        while True:
            if event_handler.last_modified > last_check:
                data = get_game_data()
                if data:
                    yield f"data: {json.dumps(data)}\n\n"
                last_check = event_handler.last_modified
            import time
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)