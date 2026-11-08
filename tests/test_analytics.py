"""This file contains unit tests for the analytics module, using the predefined habits as fixture."""

from datetime import date, datetime

import pytest

from habit_tracker import analytics
from habit_tracker.fixtures import START, predefined_habits
from habit_tracker.habit import Habit

END_OF_DATA = datetime(2026, 11, 1, 21, 0)  # Sunday evening, last day of data


@pytest.fixture
def habits():
    """Provide the five predefined habits as a dictionary keyed by name."""
    return {habit.name: habit for habit in predefined_habits()}


def test_all_habits_are_sorted_by_name(habits):
    names = [habit.name for habit in analytics.all_habits(list(habits.values()))]
    assert names == ["Call family", "Clean apartment", "Drink water", "Study", "Walking"]


def test_habits_by_periodicity(habits):
    daily = analytics.habits_by_periodicity(list(habits.values()), "daily")
    weekly = analytics.habits_by_periodicity(list(habits.values()), "Weekly")
    assert [habit.name for habit in daily] == ["Drink water", "Study", "Walking"]
    assert [habit.name for habit in weekly] == ["Call family", "Clean apartment"]


@pytest.mark.parametrize("name, expected", [
    ("Drink water", 28),
    ("Study", 10),
    ("Walking", 12),
    ("Clean apartment", 4),
    ("Call family", 2),
])
def test_longest_streak(habits, name, expected):
    assert analytics.longest_streak(habits[name]) == expected


def test_longest_streak_of_new_habit_is_zero():
    assert analytics.longest_streak(Habit("Reading", "Read 10 pages", "daily")) == 0


def test_longest_streak_overall(habits):
    assert analytics.longest_streak_overall(list(habits.values())) == ("Drink water", 28)


def test_longest_streak_overall_without_habits():
    assert analytics.longest_streak_overall([]) is None


@pytest.mark.parametrize("name, expected", [
    ("Drink water", 28),
    ("Study", 7),
    ("Walking", 12),
    ("Clean apartment", 4),
    ("Call family", 1),
])
def test_current_streak(habits, name, expected):
    assert analytics.current_streak(habits[name], now=END_OF_DATA) == expected


def test_current_streak_still_counts_while_period_is_open(habits):
    # On Monday morning the new day is not done yet, but the streak is not lost.
    next_morning = datetime(2026, 11, 2, 6, 0)
    assert analytics.current_streak(habits["Drink water"], now=next_morning) == 28


def test_current_streak_is_zero_after_a_missed_period(habits):
    two_days_later = datetime(2026, 11, 3, 12, 0)
    assert analytics.current_streak(habits["Drink water"], now=two_days_later) == 0


@pytest.mark.parametrize("name, expected", [
    ("Drink water", 0),
    ("Study", 2),
    ("Walking", 3),
    ("Clean apartment", 0),
    ("Call family", 1),
])
def test_missed_periods_in_october(habits, name, expected):
    october = (date(2026, 10, 1), date(2026, 10, 31))
    assert analytics.missed_periods(habits[name], *october) == expected


def test_struggled_habits_worst_first(habits):
    result = analytics.struggled_habits(
        list(habits.values()), date(2026, 10, 1), date(2026, 10, 31)
    )
    assert result == [("Walking", 3), ("Study", 2), ("Call family", 1)]


def test_analytics_do_not_change_habits(habits):
    before = {name: habit.completions for name, habit in habits.items()}
    analytics.longest_streak(habits["Study"])
    analytics.struggled_habits(list(habits.values()), START.date(), END_OF_DATA.date())
    assert {name: habit.completions for name, habit in habits.items()} == before


