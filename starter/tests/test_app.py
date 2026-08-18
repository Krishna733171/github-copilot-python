import pytest
from app import app, CURRENT
import sudoku_logic


@pytest.fixture
def client():
    """Setup: Create a test client that can make requests"""
    app.config['TESTING'] = True  # Enable testing mode
    with app.test_client() as test_client:
        yield test_client  # Give the test a client to use


@pytest.fixture
def with_active_game(client):
    """Setup: Start a fresh game before the test"""
    client.get('/new')  # Call /new to create puzzle and solution
    return client


class TestHomepage:
    """Tests for the homepage (/ route)"""
    
    def test_homepage_returns_success(self, client):
        """✓ Check: homepage loads with status 200 (success)"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_homepage_contains_title(self, client):
        """✓ Check: homepage HTML has 'Sudoku Game' title"""
        response = client.get('/')
        assert b'Sudoku Game' in response.data
    
    def test_homepage_has_board_div(self, client):
        """✓ Check: homepage HTML has sudoku-board element"""
        response = client.get('/')
        assert b'sudoku-board' in response.data
    
    def test_homepage_has_new_game_button(self, client):
        """✓ Check: homepage HTML has 'new-game' button"""
        response = client.get('/')
        assert b'new-game' in response.data
    
    def test_homepage_has_check_button(self, client):
        """✓ Check: homepage HTML has 'check-solution' button"""
        response = client.get('/')
        assert b'check-solution' in response.data


class TestNewGameRoute:
    """Tests for the /new route (creates puzzle)"""
    
    def test_new_game_returns_success(self, client):
        """✓ Check: /new route returns status 200 (success)"""
        response = client.get('/new')
        assert response.status_code == 200
    
    def test_new_game_returns_json(self, client):
        """✓ Check: /new response is JSON format"""
        response = client.get('/new')
        assert response.content_type == 'application/json'
    
    def test_new_game_contains_puzzle_key(self, client):
        """✓ Check: /new JSON response has 'puzzle' key"""
        response = client.get('/new')
        data = response.get_json()
        assert 'puzzle' in data
    
    def test_new_game_puzzle_is_9x9(self, client):
        """✓ Check: puzzle returned is 9x9 board"""
        response = client.get('/new')
        puzzle = response.get_json()['puzzle']
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
    
    def test_new_game_default_clues(self, client):
        """✓ Check: default /new creates puzzle with 35 clues"""
        response = client.get('/new')
        puzzle = response.get_json()['puzzle']
        filled = sum(1 for row in puzzle for cell in row if cell != 0)
        assert filled == 35
    
    def test_new_game_custom_clues(self, client):
        """✓ Check: /new?clues=40 creates puzzle with 40 clues"""
        response = client.get('/new?clues=40')
        puzzle = response.get_json()['puzzle']
        filled = sum(1 for row in puzzle for cell in row if cell != 0)
        assert filled == 40
    
    @pytest.mark.parametrize(
        "path, expected_clues",
        [
            ("/new?difficulty=easy", 45),
            ("/new?difficulty=medium", 35),
            ("/new?difficulty=hard", 26),
            ("/new", 35),          # default should be medium
            ("/new?clues=35", 35), # old behavior still works
        ],
    )
    def test_new_game_difficulty_and_default_clues(self, client, path, expected_clues):
        """Check difficulty names, default behavior, and old clues route."""
        response = client.get(path)
        puzzle = response.get_json()["puzzle"]
        filled = sum(1 for row in puzzle for cell in row if cell != 0)
        
        # Hard difficulty may be 25-27 due to unique-solution constraint
        if expected_clues == 26:
            assert 25 <= filled <= 27, f"Hard mode should have 25-27 clues, got {filled}"
        else:
            assert filled == expected_clues
    
    def test_new_game_stores_solution(self, client):
        """✓ Check: /new stores solution so /check can validate it"""
        client.get('/new')
        assert CURRENT['solution'] is not None


class TestCheckRoute:
    """Tests for /check route (validates solution)"""
    
    def test_check_without_game_returns_error(self, client):
        """✓ Check: /check without starting game returns error (400)"""
        CURRENT['solution'] = None  # Clear solution so no game is active
        response = client.post('/check', json={'board': [[0]*9 for _ in range(9)]})
        
        assert response.status_code == 400  # 400 = error
        data = response.get_json()
        assert 'error' in data  # Response has error message
    
    def test_check_with_correct_solution(self, with_active_game):
        """✓ Check: correct solution returns empty list of incorrect cells"""
        # Use the actual solution from the active game
        response = with_active_game.post('/check', json={'board': CURRENT['solution']})
        data = response.get_json()
        
        assert data['incorrect'] == []  # No mistakes
    
    def test_check_with_incorrect_cells(self, with_active_game):
        """✓ Check: wrong board identifies incorrect cells"""
        # Copy the solution but change the first cell to wrong value
        board = [row[:] for row in CURRENT['solution']]
        board[0][0] = 0  # Make it wrong
        
        response = with_active_game.post('/check', json={'board': board})
        data = response.get_json()
        
        assert [0, 0] in data['incorrect']  # Should mark [0,0] as wrong
    
    def test_check_with_multiple_incorrect_cells(self, with_active_game):
        """✓ Check: identifies multiple incorrect cells"""
        # Copy solution and change 2 cells
        board = [row[:] for row in CURRENT['solution']]
        board[0][0] = 0  # Wrong
        board[5][5] = 0  # Wrong
        
        response = with_active_game.post('/check', json={'board': board})
        data = response.get_json()
        
        assert [0, 0] in data['incorrect']
        assert [5, 5] in data['incorrect']
    
    def test_check_response_is_json(self, with_active_game):
        """✓ Check: /check response is JSON format"""
        response = with_active_game.post('/check', json={'board': CURRENT['solution']})
        assert response.content_type == 'application/json'
    
    def test_check_incorrect_is_list(self, with_active_game):
        """✓ Check: 'incorrect' in response is a list of positions"""
        response = with_active_game.post('/check', json={'board': CURRENT['solution']})
        data = response.get_json()
        assert isinstance(data['incorrect'], list)


def test_hint_returns_one_correct_cell(client):
    client.get('/new')
    response = client.post('/hint')
    assert response.status_code == 200

    data = response.get_json()
    row = data['row']
    col = data['col']
    value = data['value']

    assert 0 <= row < 9
    assert 0 <= col < 9
    assert CURRENT['puzzle'][row][col] == value
    assert CURRENT['solution'][row][col] == value


def test_hint_only_fills_empty_cell(client):
    client.get('/new')
    puzzle_before = [row[:] for row in CURRENT['puzzle']]

    response = client.post('/hint')
    data = response.get_json()

    row = data['row']
    col = data['col']

    assert puzzle_before[row][col] == 0
    assert CURRENT['puzzle'][row][col] == CURRENT['solution'][row][col]


def test_hint_does_not_reveal_entire_solution(client):
    client.get('/new')
    before = [row[:] for row in CURRENT['puzzle']]

    response = client.post('/hint')
    data = response.get_json()

    diff_count = 0
    for i in range(9):
        for j in range(9):
            if before[i][j] != CURRENT['puzzle'][i][j]:
                diff_count += 1

    assert diff_count == 1


def test_hint_without_game_returns_error(client):
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    response = client.post('/hint')
    assert response.status_code == 400

