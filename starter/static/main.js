// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let selectedDifficulty = 'medium';
let timerInterval = null;
let startTime = 0;
let elapsedSeconds = 0;

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';

  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';

    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;

      const boxRow = Math.floor(i / 3);
      const boxCol = Math.floor(j / 3);
      const isLightSquare = (boxRow + boxCol) % 2 === 0;
      input.classList.add(isLightSquare ? 'square-light' : 'square-dark');

      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
      });

      rowDiv.appendChild(input);
    }

    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame(difficulty = selectedDifficulty) {
  const url = difficulty ? `/new?difficulty=${difficulty}` : '/new';
  const res = await fetch(url);
  const data = await res.json();

  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  resetTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });

  const data = await res.json();
  const msg = document.getElementById('message');

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }

  if (incorrect.size === 0) {
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const res = await fetch('/hint', { method: 'POST' });

  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }

  const row = data.row;
  const col = data.col;
  const value = data.value;

  const input = document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
  if (!input) return;

  input.value = value;
  input.disabled = true;
  input.classList.add('prefilled');
  input.classList.remove('incorrect');

  document.getElementById('message').innerText = 'Hint used!';
}

function setTheme(isDark) {
  document.body.classList.toggle('dark', isDark);
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    toggle.textContent = isDark ? 'Light Mode' : 'Dark Mode';
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  if (timerEl) {
    timerEl.textContent = formatTime(elapsedSeconds);
  }
}

function resetTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  startTime = Date.now();
  updateTimerDisplay();

  timerInterval = setInterval(() => {
    elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
}

window.addEventListener('load', () => {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  setTheme(prefersDark);

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isDark = !document.body.classList.contains('dark');
      setTheme(isDark);
    });
  }

  document.getElementById('easy-btn').addEventListener('click', () => {
    selectedDifficulty = 'easy';
    newGame(selectedDifficulty);
  });

  document.getElementById('medium-btn').addEventListener('click', () => {
    selectedDifficulty = 'medium';
    newGame(selectedDifficulty);
  });

  document.getElementById('hard-btn').addEventListener('click', () => {
    selectedDifficulty = 'hard';
    newGame(selectedDifficulty);
  });

  document.getElementById('new-game').addEventListener('click', () => {
    newGame(selectedDifficulty);
  });

  document.getElementById('check-solution').addEventListener('click', checkSolution);

  document.getElementById('hint-btn').addEventListener('click', async () => {
    const res = await fetch('/hint', { method: 'POST' });
    const data = await res.json();

    if (data.error) {
      document.getElementById('message').innerText = data.error;
      return;
    }

    const row = data.row;
    const col = data.col;
    const value = data.value;

    const input = document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
    if (!input) return;

    input.value = value;
    input.disabled = true;
    input.classList.add('prefilled');
  });

  newGame(selectedDifficulty);
});