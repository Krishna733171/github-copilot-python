from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty_map = {
        'easy': 45,
        'medium': 35,
        'hard': 26
    }

    clues = request.args.get('clues')
    difficulty = request.args.get('difficulty')

    if clues is not None:
        clues = int(clues)
    elif difficulty is not None:
        clues = difficulty_map.get(difficulty.lower(), difficulty_map['medium'])
    else:
        clues = difficulty_map['medium']

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint', methods=['POST'])
def get_hint():
    if CURRENT.get('solution') is None or CURRENT.get('puzzle') is None:
        return jsonify({'error': 'No game in progress'}), 400

    puzzle = CURRENT['puzzle']
    solution = CURRENT['solution']

    empty_cells = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == 0:
                empty_cells.append((row, col))

    if not empty_cells:
        return jsonify({'error': 'No empty cells available'}), 400

    row, col = empty_cells[0]
    value = solution[row][col]
    puzzle[row][col] = value
    CURRENT['puzzle'] = puzzle

    return jsonify({'row': row, 'col': col, 'value': value})

if __name__ == '__main__':
    app.run(debug=True)