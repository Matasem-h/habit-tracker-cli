"""This file contains unit tests for the analytics module, using the predefined habits as fixture."""

from datetime import date, datetime

import pytest

from habit_tracker import analytics
from habit_tracker.fixtures import predefined_habits
from habit_tracker.habit import Habit


@pytest.fixture
def habits():
    """Provide a fresh copy of the five predefined habits."""
    return predefined_habits()


def by_name(habits, name):
    """Return the habit with the given name from a list."""
    return next(habit for habit in habits if habit.name == name)


def test_habit_names_are_sorted(habits):
    assert analytics.habit_names(habits) == [
        "Call family", "Clean apartment", "Drink water", "Study", "Walking",
    ]


def test_daily_habits(habits):
    assert analytics.habits_with_periodicity(habits, "daily") == [
        "Drink water", "Study", "Walking",
    ]


def test_weekly_habits_ignore_case(habits):
    assert analytics.habits_with_periodicity(habits, "Weekly") == [
        "Call family", "Clean apartment",
    ]


@pytest.mark.parametrize("name, expected", [
    ("Drink water", 28),
    ("Study", 10),
    ("Walking", 12),
    ("Clean apartment", 4),
    ("Call family", 2),
])
def test_longest_streak_per_habit(habits, name, expected):
    assert analytics.longest_streak_for(habits, name) == expected


def test_longest_streak_overall(habits):
    assert analytics.longest_streak_overall(habits) == ("Drink water", 28)


def test_longest_streak_overall_without_habits():
    assert analytics.longest_streak_overall([]) == (None, 0)


def test_longest_streak_for_unknown_habit(habits):
    with pytest.raises(KeyError):
        analytics.longest_streak_for(habits, "Nothing")


def test_habit_without_completions_has_no_streak():
    habit = Habit("Reading", "Read 10 pages", "daily", datetime(2026, 10, 5))
    assert analytics.longest_streak(habit) == 0


def test_current_streak_counts_back_from_today(habits):
    # Sunday 1 Nov is the last fixture day; Walking was done every day since 21 Oct.
    now = datetime(2026, 11, 1, 22, 0)
    assert analytics.current_streak(by_name(habits, "Walking"), now) == 12


def test_current_streak_still_counts_before_todays_check_off(habits):
    # Early on 2 Nov, today is not done yet but yesterday's streak still holds.
    now = datetime(2026, 11, 2, 6, 0)
    assert analytics.current_streak(by_name(habits, "Drink water"), now) == 28


def test_current_streak_is_zero_after_a_missed_period(habits):
    now = datetime(2026, 11, 4, 12, 0)
    assert analytics.current_streak(by_name(habits, "Study"), now) == 0


def test_struggled_habits_in_october(habits):
    result = analytics.struggled_habits(habits, date(2026, 10, 1), date(2026, 11, 1))
    assert result == [("Walking", 3), ("Study", 2), ("Call family", 1)]


def test_analytics_do_not_change_the_habits(habits):
    before = [habit.completions for habit in habits]
    analytics.longest_streak_overall(habits)
    analytics.struggled_habits(habits, date(2026, 10, 1), date(2026, 11, 1))
    assert [habit.completions for habit in habits] == before


