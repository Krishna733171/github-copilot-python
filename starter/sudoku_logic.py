import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if sum(1 for r in board for value in r if value != EMPTY) <= clues:
            break

        if board[row][col] == EMPTY:
            continue

        saved_value = board[row][col]
        board[row][col] = EMPTY

        # Keep the removal only if the puzzle still has exactly one solution
        if count_solutions(board, limit=2) != 1:
            board[row][col] = saved_value

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution

def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None

def count_solutions(board, limit=2):
    empty_cell = find_empty_cell(board)

    # No empty cells left -> one complete solution found
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solutions = 0

    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            board[row][col] = num
            solutions += count_solutions(board, limit)
            board[row][col] = EMPTY

            if solutions >= limit:
                return solutions

    return solutions
