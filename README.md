# Habit Tracker CLI

A command-line habit tracker built in Python. Define daily or weekly habits, check them off, and analyze your streaks.

This is a university portfolio project for the course *Object-Oriented and Functional Programming with Python*.
It combines:

- **Object-oriented programming** for the habit model (`Habit` class)
- **Functional programming** for the analytics (pure functions using `map`, `filter`, `reduce`)
- **SQLite** for storing data between sessions
- **click** for the command-line interface
- **pytest** for the unit tests

## Requirements

- Python 3.7 or later
- The packages in `requirements.txt` (`click` and `pytest`)

## Installation

1. Download the project, either with Git:

   ```
   git clone https://github.com/Matasem-h/habit-tracker-cli.git
   cd habit-tracker-cli
   ```

   or by downloading it as a ZIP from GitHub and extracting it.

2. Create and activate a virtual environment.

   **Windows (PowerShell):**

   ```
   py -m venv .venv
   & ".\.venv\Scripts\Activate.ps1"
   ```

   **macOS / Linux:**

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Your prompt now starts with `(.venv)`.

3. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

## Quick start

Load the five example habits and look at them:

```
python -m habit_tracker load-examples
python -m habit_tracker list
```

The example data covers the four weeks from 5 October to 1 November 2026. If you run the app after that, 
the example habits show as "streak broken" until you check them off again.

## Usage

Every command follows the pattern `python -m habit_tracker COMMAND [OPTIONS]`.
Add `--help` to any command for details, e.g. `python -m habit_tracker add --help`.

| Command | What it does |
|---|---|
| `add NAME` | Create a new habit |
| `complete NAME` | Check off a habit for the current period |
| `list` | List all habits with their current streak and status |
| `show NAME` | Show the details and statistics of one habit |
| `streak [NAME]` | Show the longest streak of all habits, or of one habit |
| `struggled` | Show which habits were missed most often in a month |
| `delete NAME` | Delete a habit and all its check-offs |
| `load-examples` | Load the five predefined habits with example data |

Put habit names that contain spaces in quotes, e.g. `"Drink water"`.

### Create a habit

```
python -m habit_tracker add Reading -d "Read 10 pages" -p daily
```

- `-d` / `--description`: what the task is
- `-p` / `--periodicity`: `daily` or `weekly`

If you leave out `-d` or `-p`, the app asks for them.

### Complete a habit

```
python -m habit_tracker complete Reading
```

A habit must be checked off **at least once per period** to keep its streak:

- **Daily** habits: once per calendar day.
- **Weekly** habits: once per calendar week (Monday to Sunday).

Checking off a habit twice in the same period counts only once; the app tells you it is already done.

### View your habits

```
python -m habit_tracker list
python -m habit_tracker list -p weekly
python -m habit_tracker show Reading
```

`list` shows each habit's current streak and whether it is `done` or still `open` in the current period.
A habit is marked `streak broken` if the previous period was missed.

### Analyze your habits

```
python -m habit_tracker streak
python -m habit_tracker streak Reading
python -m habit_tracker struggled
python -m habit_tracker struggled -m 2026-10
```

- `streak` without a name shows the longest streak across all habits.
- `struggled` lists the habits with missed periods last month, most missed first. Use `-m YYYY-MM` for another month.

### Delete a habit

```
python -m habit_tracker delete Reading
```

The app asks for confirmation. Add `--yes` to skip it.

### Database location

Data is stored in `habits.db` in the folder you run the commands from.
To use a different file, put `--db` before the command:

```
python -m habit_tracker --db my_habits.db list
```

## Running the tests

```
python -m pytest
```

The test suite covers the `Habit` class, the storage layer, the example data, the analytics module and the command-line interface.
The analytics tests use the five predefined habits as a test fixture, so their expected streaks are known in advance:

| Habit | Periodicity | Longest streak |
|---|---|---|
| Drink water | daily | 28 days |
| Study | daily | 10 days |
| Walking | daily | 12 days |
| Clean apartment | weekly | 4 weeks |
| Call family | weekly | 2 weeks |

## Project structure

```
habit-tracker-cli/
├── habit_tracker/
│   ├── __init__.py
│   ├── __main__.py     # entry point for "python -m habit_tracker"
│   ├── habit.py        # Habit class (object-oriented)
│   ├── storage.py      # SQLite storage layer
│   ├── analytics.py    # analytics (functional programming)
│   ├── fixtures.py     # five predefined habits with four weeks of data
│   └── cli.py          # click command-line interface
├── tests/              # pytest unit tests, one file per module
├── requirements.txt
└── README.md
```

Each module has one responsibility.
The command-line interface only handles input and output, so the `Habit` class, storage layer and analytics module
could be reused unchanged by a different interface, such as a graphical or web front end.


## Author: Matasem Habibullah, IU International University of Applied Sciences


