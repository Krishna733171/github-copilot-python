import pytest
import sudoku_logic


class TestPuzzleGeneration:
    """Tests for puzzle generation"""
    
    def test_generate_puzzle_returns_two_values(self):
        """✓ Check: generate_puzzle() returns (puzzle, solution)"""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        assert puzzle is not None
        assert solution is not None
    
    def test_puzzle_is_9_by_9(self):
        """✓ Check: puzzle board is 9 rows x 9 columns"""
        puzzle, _ = sudoku_logic.generate_puzzle(clues=35)
        assert len(puzzle) == 9  # 9 rows
        assert all(len(row) == 9 for row in puzzle)  # 9 columns each
    
    def test_solution_is_9_by_9(self):
        """✓ Check: solution board is 9 rows x 9 columns"""
        _, solution = sudoku_logic.generate_puzzle(clues=35)
        assert len(solution) == 9
        assert all(len(row) == 9 for row in solution)
    
    def test_puzzle_has_correct_number_of_clues(self):
        """✓ Check: puzzle has exactly the requested number of filled cells"""
        clues_wanted = 30
        puzzle, _ = sudoku_logic.generate_puzzle(clues=clues_wanted)
        
        # Count cells that are filled (not 0)
        filled_cells = sum(1 for row in puzzle for cell in row if cell != 0)
        
        assert filled_cells == clues_wanted
    
    def test_solution_is_completely_filled(self):
        """✓ Check: solution has all 81 cells filled (no zeros)"""
        _, solution = sudoku_logic.generate_puzzle(clues=35)
        
        # Count cells that are filled
        filled_cells = sum(1 for row in solution for cell in row if cell != 0)
        
        assert filled_cells == 81  # 9x9 = 81 total cells
    
    def test_puzzle_clues_match_solution(self):
        """✓ Check: all pre-filled puzzle cells match the solution"""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:  # If this cell has a clue
                    assert puzzle[i][j] == solution[i][j]  # It must match solution


class TestSafetyCheck:
    """Tests for is_safe() validation function"""
    
    def test_is_safe_on_empty_board(self):
        """✓ Check: any number is safe on completely empty board"""
        board = [[0] * 9 for _ in range(9)]
        assert sudoku_logic.is_safe(board, 0, 0, 5) is True
    
    def test_is_safe_rejects_duplicate_in_row(self):
        """✓ Check: rejects number that's already in same row"""
        board = [[0] * 9 for _ in range(9)]
        board[0][1] = 5  # Put 5 at position [0][1]
        # Try to place 5 at [0][0] (same row) - should fail
        assert sudoku_logic.is_safe(board, 0, 0, 5) is False
    
    def test_is_safe_rejects_duplicate_in_column(self):
        """✓ Check: rejects number that's already in same column"""
        board = [[0] * 9 for _ in range(9)]
        board[1][0] = 5  # Put 5 at position [1][0]
        # Try to place 5 at [0][0] (same column) - should fail
        assert sudoku_logic.is_safe(board, 0, 0, 5) is False
    
    def test_is_safe_rejects_duplicate_in_3x3_box(self):
        """✓ Check: rejects number that's already in same 3x3 box"""
        board = [[0] * 9 for _ in range(9)]
        board[1][1] = 5  # Put 5 in top-left 3x3 box
        # Try to place 5 at [0][0] (same 3x3 box) - should fail
        assert sudoku_logic.is_safe(board, 0, 0, 5) is False
    
    def test_is_safe_allows_number_in_different_box(self):
        """✓ Check: allows number if it's in a different 3x3 box"""
        board = [[0] * 9 for _ in range(9)]
        board[0][1] = 5  # Put 5 in top-left 3x3 box
        # Place 5 at [3][3] (middle-middle 3x3 box, different row AND column) - should work
        assert sudoku_logic.is_safe(board, 3, 3, 5) is True

def test_generated_puzzle_has_one_unique_solution():
    """Check that a generated puzzle has exactly one solution."""
    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

    solution_count = sudoku_logic.count_solutions(puzzle, limit=2)

    assert solution_count == 1