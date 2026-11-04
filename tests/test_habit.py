"""Unit tests for the Habit class."""

from datetime import date, datetime

import pytest

from habit_tracker.habit import Habit

CREATED = datetime(2026, 10, 5, 8, 0)  # a Monday


def make(periodicity="daily", completions=None):
    """Build a habit created on CREATED, optionally with completions."""
    return Habit("Walking", "Walk for 30 minutes", periodicity, CREATED, completions)


class TestCreation:
    def test_stores_all_fields(self):
        habit = make()
        assert habit.name == "Walking"
        assert habit.description == "Walk for 30 minutes"
        assert habit.periodicity == "daily"
        assert habit.created_at == CREATED
        assert habit.completions == ()

    def test_periodicity_is_case_insensitive(self):
        assert make("Weekly").periodicity == "weekly"

    def test_rejects_unknown_periodicity(self):
        with pytest.raises(ValueError):
            make("monthly")

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError):
            Habit("   ", "something", "daily")

    def test_created_at_defaults_to_now(self):
        before = datetime.now()
        habit = Habit("Reading", "Read 10 pages", "daily")
        assert before <= habit.created_at <= datetime.now()


class TestCompletion:
    def test_complete_records_timestamp(self):
        habit = make()
        when = datetime(2026, 10, 6, 7, 30)
        assert habit.complete(when) == when
        assert habit.completions == (when,)

    def test_completions_are_kept_sorted(self):
        habit = make()
        later, earlier = datetime(2026, 10, 9), datetime(2026, 10, 7)
        habit.complete(later)
        habit.complete(earlier)
        assert habit.completions == (earlier, later)

    def test_cannot_complete_before_creation(self):
        with pytest.raises(ValueError):
            make().complete(datetime(2026, 10, 1))

    def test_completions_cannot_be_modified_from_outside(self):
        habit = make()
        with pytest.raises(AttributeError):
            habit.completions.append(datetime(2026, 10, 6))


class TestPeriods:
    def test_daily_period_is_the_calendar_day(self):
        assert make().period_start(datetime(2026, 10, 8, 23, 59)) == date(2026, 10, 8)

    def test_weekly_period_starts_on_monday(self):
        sunday = datetime(2026, 10, 11, 20, 0)
        assert make("weekly").period_start(sunday) == date(2026, 10, 5)

    def test_is_completed_in_period(self):
        habit = make("weekly", [datetime(2026, 10, 7, 18, 0)])
        assert habit.is_completed_in_period(datetime(2026, 10, 11))
        assert not habit.is_completed_in_period(datetime(2026, 10, 12))


class TestBroken:
    def test_new_habit_is_not_broken(self):
        assert not make().is_broken(now=datetime(2026, 10, 5, 22, 0))

    def test_daily_broken_when_yesterday_missed(self):
        habit = make(completions=[datetime(2026, 10, 5, 9, 0)])
        assert habit.is_broken(now=datetime(2026, 10, 7, 9, 0))

    def test_daily_not_broken_when_yesterday_done(self):
        habit = make(completions=[datetime(2026, 10, 6, 9, 0)])
        assert not habit.is_broken(now=datetime(2026, 10, 7, 9, 0))

    def test_weekly_broken_when_last_week_missed(self):
        habit = make("weekly", [datetime(2026, 10, 6, 9, 0)])
        assert habit.is_broken(now=datetime(2026, 10, 20, 9, 0))

    def test_weekly_not_broken_when_last_week_done(self):
        habit = make("weekly", [datetime(2026, 10, 15, 9, 0)])
        assert not habit.is_broken(now=datetime(2026, 10, 20, 9, 0))
