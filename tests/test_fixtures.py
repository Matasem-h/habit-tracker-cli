"""This file contains unit tests for the predefined habits and their example data."""

from datetime import timedelta

from habit_tracker.fixtures import START, load_predefined_habits, predefined_habits
from habit_tracker.storage import HabitStorage


def test_there_are_five_habits_with_unique_names():
    names = [habit.name for habit in predefined_habits()]
    assert len(names) == 5
    assert len(set(names)) == 5


def test_both_periodicities_are_included():
    periodicities = {habit.periodicity for habit in predefined_habits()}
    assert periodicities == {"daily", "weekly"}


def test_all_data_lies_within_four_weeks():
    end = START + timedelta(weeks=4)
    for habit in predefined_habits():
        assert habit.completions
        assert all(START <= done < end for done in habit.completions)


def test_daily_habit_completion_counts():
    counts = {habit.name: len(habit.completions) for habit in predefined_habits()}
    assert counts["Drink water"] == 28
    assert counts["Study"] == 26
    assert counts["Walking"] == 25


def test_weekly_habit_completion_counts():
    counts = {habit.name: len(habit.completions) for habit in predefined_habits()}
    assert counts["Clean apartment"] == 4
    assert counts["Call family"] == 3


def test_loading_saves_all_habits():
    with HabitStorage(":memory:") as storage:
        assert load_predefined_habits(storage) == 5
        assert len(storage.get_all_habits()) == 5


def test_loading_twice_adds_no_duplicates():
    with HabitStorage(":memory:") as storage:
        load_predefined_habits(storage)
        assert load_predefined_habits(storage) == 0
        assert len(storage.get_all_habits()) == 5


