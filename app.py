from flask import Flask
from flask import render_template
from flask import jsonify 
from flask import request
import random

app = Flask(__name__)

# Global variable to hold the game state
game_state = [""] * 9
current_turn = "X"

# Function to check for a winner or tie
def check_winner():
    winning_combos = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    
    for combo in winning_combos:
        if game_state[combo[0]] == game_state[combo[1]] == game_state[combo[2]] != "":
            return game_state[combo[0]]
    
    if "" not in game_state:
        return "Tie"
    
    return None

# Minimax algorithm for AI move
def minimax(state, depth, is_maximizing):
    scores = {'X': -1, 'O': 1, 'Tie': 0}
    winner = check_winner()
    if winner in scores:
        return scores[winner]
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if state[i] == "":
                state[i] = 'O'
                score = minimax(state, depth + 1, False)
                state[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if state[i] == "":
                state[i] = 'X'
                score = minimax(state, depth + 1, True)
                state[i] = ""
                best_score = min(score, best_score)
        return best_score

def ai_move():
    best_score = -float('inf')
    move = -1
    for i in range(9):
        if game_state[i] == "":
            game_state[i] = 'O'
            score = minimax(game_state, 0, False)
            game_state[i] = ""
            if score > best_score:
                best_score = score
                move = i
    return move

# Home route - displays the Tic-Tac-Toe board
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle player moves
@app.route('/move', methods=['POST'])
def move():
    global current_turn, game_state
    position = int(request.json['position'])
    
    if game_state[position] == "":
        game_state[position] = current_turn
        winner = check_winner()
        
        if winner:
            return jsonify({"winner": winner, "game_state": game_state})
        
        # AI's turn
        ai_position = ai_move()
        game_state[ai_position] = "O"
        winner = check_winner()
        
        if winner:
            return jsonify({"winner": winner, "game_state": game_state})
        
        # Switch the turn
        current_turn = "X"
        return jsonify({"game_state": game_state, "turn": current_turn})
    
    return jsonify({"error": "Invalid move"})

# Route to reset the game
@app.route('/reset', methods=['POST'])
def reset():
    global game_state, current_turn
    game_state = [""] * 9
    current_turn = "X"
    return jsonify({"message": "Game reset", "game_state": game_state})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)