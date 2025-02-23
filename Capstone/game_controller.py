import sqlite3
from darts_cv_simulation import DartDetection
import time

class DartGameController:
    def __init__(self, db_path='simple_dartboard.db'):
        self.db_path = db_path
        self.dart_detector = DartDetection()
        
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_current_game_state(self):
        """Get the current game state from the database"""
        conn = self.get_db_connection()
        try:
            # Get active game and current player
            game = conn.execute('''
                SELECT g.*, p.player_name, p.player_order, p.current_score
                FROM games g
                JOIN players p ON g.current_player_id = p.player_id
                WHERE g.game_status = 'active'
                ORDER BY g.game_id DESC LIMIT 1
            ''').fetchone()
            
            if not game:
                raise Exception("No active game found")
                
            return dict(game)
        finally:
            conn.close()

    def get_current_round_throws(self, game_id, player_id):
        """Get number of throws in current round"""
        conn = self.get_db_connection()
        try:
            # Get the latest round
            round_data = conn.execute('''
                SELECT * FROM rounds 
                WHERE game_id = ? AND player_id = ?
                ORDER BY round_number DESC LIMIT 1
            ''', [game_id, player_id]).fetchone()
            
            if not round_data:
                return 0, 1  # No throws, round 1
                
            # Count non-null throws
            throws = 0
            if round_data['first_throw'] is not None: throws += 1
            if round_data['second_throw'] is not None: throws += 2
            if round_data['third_throw'] is not None: throws += 3
                
            if throws == 3:  # Round complete
                return 0, round_data['round_number'] + 1
            return throws, round_data['round_number']
        finally:
            conn.close()

    def get_next_player(self, game_id, current_player_order):
        """Get the next player in sequence"""
        conn = self.get_db_connection()
        try:
            # Get total number of players
            total_players = conn.execute('''
                SELECT COUNT(*) as count FROM players WHERE game_id = ?
            ''', [game_id]).fetchone()['count']
            
            next_order = current_player_order % total_players + 1
            
            next_player = conn.execute('''
                SELECT player_id FROM players
                WHERE game_id = ? AND player_order = ?
            ''', [game_id, next_order]).fetchone()
            
            return next_player['player_id']
        finally:
            conn.close()

    def update_game_state(self, throw_score):
        """Update the game state with a new throw"""
        conn = self.get_db_connection()
        try:
            conn.execute('BEGIN TRANSACTION')
            
            # Get current game state
            game = self.get_current_game_state()
            throws, round_number = self.get_current_round_throws(game['game_id'], game['current_player_id'])
            
            # Get or create current round
            round_data = conn.execute('''
                SELECT * FROM rounds 
                WHERE game_id = ? AND player_id = ? AND round_number = ?
            ''', [game['game_id'], game['current_player_id'], round_number]).fetchone()
            
            if not round_data:
                conn.execute('''
                    INSERT INTO rounds (game_id, player_id, round_number)
                    VALUES (?, ?, ?)
                ''', [game['game_id'], game['current_player_id'], round_number])
                
            # Update the appropriate throw
            new_score = game['current_score'] - throw_score
            if new_score < 0:  # Bust
                new_score = game['current_score']
                print(f"BUST! Score would go below 0. Staying at {new_score}")
            
            if throws == 0:
                conn.execute('''
                    UPDATE rounds 
                    SET first_throw = ?, remaining_score = ?
                    WHERE game_id = ? AND player_id = ? AND round_number = ?
                ''', [throw_score, new_score, game['game_id'], game['current_player_id'], round_number])
            elif throws == 1:
                conn.execute('''
                    UPDATE rounds 
                    SET second_throw = ?, remaining_score = ?
                    WHERE game_id = ? AND player_id = ? AND round_number = ?
                ''', [throw_score, new_score, game['game_id'], game['current_player_id'], round_number])
            elif throws == 2:
                conn.execute('''
                    UPDATE rounds 
                    SET third_throw = ?, remaining_score = ?
                    WHERE game_id = ? AND player_id = ? AND round_number = ?
                ''', [throw_score, new_score, game['game_id'], game['current_player_id'], round_number])
            
            # Update player's current score
            conn.execute('''
                UPDATE players
                SET current_score = ?
                WHERE player_id = ?
            ''', [new_score, game['current_player_id']])
            
            # If this was the third throw, move to next player
            if throws == 2:
                next_player_id = self.get_next_player(game['game_id'], game['player_order'])
                conn.execute('''
                    UPDATE games
                    SET current_player_id = ?
                    WHERE game_id = ?
                ''', [next_player_id, game['game_id']])
            
            # Check for winner
            if new_score == 0:
                conn.execute('''
                    UPDATE games
                    SET game_status = 'completed'
                    WHERE game_id = ?
                ''', [game['game_id']])
                print(f"GAME OVER! {game['player_name']} wins!")
                
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def run_game(self):
        """Main game loop"""
        print("Initializing dart detection...")
        self.dart_detector.initialize()
        self.dart_detector.start()
        
        try:
            while True:
                game = self.get_current_game_state()
                if game['game_status'] == 'completed':
                    print("Game is completed!")
                    break
                    
                print(f"\nWaiting for {game['player_name']}'s throw... (Current score: {game['current_score']})")
                throw_data = self.dart_detector.get_next_throw()
                
                if throw_data:
                    score, multiplier, _ = throw_data
                    total_score = score * multiplier
                    print(f"Detected throw: {score} x {multiplier} = {total_score}")
                    
                    self.update_game_state(total_score)
                
        except KeyboardInterrupt:
            print("\nStopping game...")
        finally:
            self.dart_detector.stop()

if __name__ == "__main__":
    controller = DartGameController()
    controller.run_game()