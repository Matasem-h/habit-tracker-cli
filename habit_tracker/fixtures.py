"""This file contains five predefined habits with four weeks of example tracking data.

The data covers the four weeks from Monday 5 October to Sunday 1 November 2026.
It is fixed rather than random, so the expected streaks are known in advance and can be used as a test fixture:

================  ======  ======================  ==============
Habit             Period  Missed                  Longest streak
================  ======  ======================  ==============
Drink water       daily   nothing                 28 days
Study             daily   14 and 25 Oct           10 days
Walking           daily   8, 9 and 20 Oct         12 days
Clean apartment   weekly  nothing                 4 weeks
Call family       weekly  week of 19 Oct          2 weeks
================  ======  ======================  ==============
"""

from datetime import datetime, timedelta
from typing import Iterable, List

from habit_tracker.habit import DAILY, WEEKLY, Habit
from habit_tracker.storage import HabitStorage

START = datetime(2026, 10, 5, 7, 0)  # a Monday
DAYS = 28
WEEKS = 4


def _daily(missed_days: Iterable[int], hour: int) -> List[datetime]:
    """This returns one check-off per day for four weeks, while skipping the missed days.

    Days are counted from 0, so day 0 is the first Monday.
    """
    return [
        START.replace(hour=hour) + timedelta(days=day)
        for day in range(DAYS)
        if day not in missed_days
    ]


def _weekly(missed_weeks: Iterable[int], weekday: int, hour: int) -> List[datetime]:
    """This returns one check-off per week for four weeks, while skipping the missed weeks.

    Weeks are counted from 0; ``weekday`` is 0 for Monday up to 6 for Sunday.
    """
    return [
        START.replace(hour=hour) + timedelta(weeks=week, days=weekday)
        for week in range(WEEKS)
        if week not in missed_weeks
    ]


def predefined_habits() -> List[Habit]:
    """This returns the five predefined habits, with each having four weeks of data."""
    return [
        Habit("Drink water", "Drink 2 litres of water", DAILY, START, _daily([], 9)),
        Habit("Study", "Study for one hour", DAILY, START, _daily([9, 20], 18)),
        Habit("Walking", "Walk for 30 minutes", DAILY, START, _daily([3, 4, 15], 7)),
        Habit("Clean apartment", "Clean the whole apartment", WEEKLY, START,
              _weekly([], weekday=5, hour=11)),
        Habit("Call family", "Call the family", WEEKLY, START,
              _weekly([2], weekday=6, hour=20)),
    ]


def load_predefined_habits(storage: HabitStorage) -> int:
    """This saves the predefined habits that are not stored yet.
    Habits that already exist are left untouched, so calling this twice does not create duplicates.

    Returns:
        The number of habits that were added.
    """
    added = 0
    for habit in predefined_habits():
        if storage.get_habit(habit.name) is None:
            storage.add_habit(habit)
            added += 1
    return added


