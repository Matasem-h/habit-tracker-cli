"""SQLite storage layer: saves and loads habits between sessions."""

import sqlite3
from datetime import datetime
from typing import List, Optional

from habit_tracker.habit import Habit

DEFAULT_DB_PATH = "habits.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS habits (
    name        TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    periodicity TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_name   TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    FOREIGN KEY  (habit_name) REFERENCES habits(name) ON DELETE CASCADE
);
"""


class HabitStorage:
    """Stores habits and their completions in an SQLite database.

    This is the only part of the application that writes SQL.
    Dates are stored as ISO 8601 text, e.g. "2026-10-05T08:00:00".

    It can be used as a context manager that automatically closes the connection::

        with HabitStorage("habits.db") as storage:
            storage.add_habit(habit)
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """Open the database and create the tables if they do not exist.

        Args:
            db_path: Path to the database file.
            Use ":memory:" for a temporary database, e.g. in tests.
        """
        self._connection = sqlite3.connect(db_path)
        # SQLite only enforces foreign keys (and the cascade) when asked to.
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.executescript(SCHEMA)

    def add_habit(self, habit: Habit) -> None:
        """Save a new habit, including any completions it already has.

        Raises:
            ValueError: If a habit with the same name already exists.
        """
        try:
            with self._connection:
                self._connection.execute(
                    "INSERT INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
                    (habit.name, habit.description, habit.periodicity, habit.created_at.isoformat()),
                )
                self._connection.executemany(
                    "INSERT INTO completions (habit_name, completed_at) VALUES (?, ?)",
                    [(habit.name, done.isoformat()) for done in habit.completions],
                )
        except sqlite3.IntegrityError:
            raise ValueError("A habit named '{}' already exists.".format(habit.name))

    def add_completion(self, name: str, when: datetime) -> None:
        """Save one check-off for the habit with the given name.

        Raises:
            KeyError: If no habit with that name exists.
        """
        self._require_habit(name)
        with self._connection:
            self._connection.execute(
                "INSERT INTO completions (habit_name, completed_at) VALUES (?, ?)",
                (name, when.isoformat()),
            )

    def get_habit(self, name: str) -> Optional[Habit]:
        """Return the habit with the given name, or None if it does not exist."""
        row = self._connection.execute(
            "SELECT name, description, periodicity, created_at "
            "FROM habits WHERE name = ?",
            (name,),
        ).fetchone()
        return self._build_habit(row) if row else None

    def get_all_habits(self) -> List[Habit]:
        """Return every stored habit, sorted by name."""
        rows = self._connection.execute(
            "SELECT name, description, periodicity, created_at "
            "FROM habits ORDER BY name"
        ).fetchall()
        return [self._build_habit(row) for row in rows]

    def delete_habit(self, name: str) -> None:
        """Delete a habit and, through the cascade, all of its completions.

        Raises:
            KeyError: If no habit with that name exists.
        """
        self._require_habit(name)
        with self._connection:
            self._connection.execute("DELETE FROM habits WHERE name = ?", (name,))

    def close(self) -> None:
        """Close the database connection."""
        self._connection.close()

    def __enter__(self) -> "HabitStorage":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def _require_habit(self, name: str) -> None:
        """Raise KeyError if no habit with the given name exists."""
        found = self._connection.execute(
            "SELECT 1 FROM habits WHERE name = ?", (name,)
        ).fetchone()
        if not found:
            raise KeyError("No habit named '{}' exists.".format(name))

    def _build_habit(self, row: tuple) -> Habit:
        """Rebuild a Habit object, with its completions, from a database row."""
        name, description, periodicity, created_at = row
        completions = self._connection.execute(
            "SELECT completed_at FROM completions WHERE habit_name = ?", (name,)
        ).fetchall()
        return Habit(
            name,
            description,
            periodicity,
            created_at=datetime.fromisoformat(created_at),
            completions=[datetime.fromisoformat(done) for (done,) in completions],
        )


