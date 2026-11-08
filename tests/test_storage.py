"""Unit tests for the SQLite storage layer."""

from datetime import datetime

import pytest

from habit_tracker.habit import Habit
from habit_tracker.storage import HabitStorage

CREATED = datetime(2026, 10, 5, 8, 0)


@pytest.fixture
def storage():
    """Provide a fresh in-memory database for each test."""
    with HabitStorage(":memory:") as db:
        yield db


def make(name="Walking", completions=None):
    """Build a daily habit created on CREATED."""
    return Habit(name, "Walk for 30 minutes", "daily", CREATED, completions)


def test_saved_habit_can_be_loaded(storage):
    storage.add_habit(make())
    loaded = storage.get_habit("Walking")
    assert loaded.name == "Walking"
    assert loaded.description == "Walk for 30 minutes"
    assert loaded.periodicity == "daily"
    assert loaded.created_at == CREATED


def test_existing_completions_are_saved(storage):
    done = [datetime(2026, 10, 6, 9, 0), datetime(2026, 10, 7, 9, 0)]
    storage.add_habit(make(completions=done))
    assert storage.get_habit("Walking").completions == tuple(done)


def test_duplicate_name_is_rejected(storage):
    storage.add_habit(make())
    with pytest.raises(ValueError):
        storage.add_habit(make())


def test_unknown_habit_returns_none(storage):
    assert storage.get_habit("Nothing") is None


def test_add_completion(storage):
    storage.add_habit(make())
    when = datetime(2026, 10, 8, 7, 30)
    storage.add_completion("Walking", when)
    assert storage.get_habit("Walking").completions == (when,)


def test_add_completion_to_unknown_habit_fails(storage):
    with pytest.raises(KeyError):
        storage.add_completion("Nothing", datetime(2026, 10, 8))


def test_get_all_habits_is_sorted_by_name(storage):
    storage.add_habit(make("Reading"))
    storage.add_habit(make("Cooking"))
    names = [habit.name for habit in storage.get_all_habits()]
    assert names == ["Cooking", "Reading"]


def test_delete_removes_habit_and_completions(storage):
    storage.add_habit(make(completions=[datetime(2026, 10, 6, 9, 0)]))
    storage.delete_habit("Walking")
    assert storage.get_habit("Walking") is None
    count = storage._connection.execute("SELECT COUNT(*) FROM completions").fetchone()
    assert count == (0,)


def test_delete_unknown_habit_fails(storage):
    with pytest.raises(KeyError):
        storage.delete_habit("Nothing")


def test_data_persists_between_sessions(tmp_path):
    db_file = str(tmp_path / "habits.db")
    with HabitStorage(db_file) as first_session:
        first_session.add_habit(make())
    with HabitStorage(db_file) as second_session:
        assert second_session.get_habit("Walking") is not None
