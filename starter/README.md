# Sudoku Game

A web-based Sudoku puzzle game built with Flask and vanilla JavaScript. Features difficulty selection, a timer, hints, and a persistent Top 10 scoreboard using browser localStorage.

## Features

- **3 Difficulty Levels**: Easy (45 clues), Medium (35 clues), Hard (26 clues)
- **Unique Solutions**: Every puzzle is mathematically guaranteed to have exactly one solution
- **Timer**: Tracks completion time for scoring
- **Hint System**: Reveals one correct empty cell per request
- **Top 10 Scoreboard**: Persistent leaderboard stored in browser localStorage
- **Responsive Design**: Works on desktop and mobile devices
- **Light/Dark Mode**: Theme toggle for comfortable gameplay
- **Real-time Validation**: Instant feedback on cell correctness

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt