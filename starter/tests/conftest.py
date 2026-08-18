import sys
from pathlib import Path

# Add starter directory to Python path so we can import app and sudoku_logic
# conftest.py is in: starter/tests/conftest.py
# .parent = starter/tests/
# .parent.parent = starter/
STARTER_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(STARTER_DIR))