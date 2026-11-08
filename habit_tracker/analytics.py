"""This file is the analytics module, it answers questions about habits using functional programming.

Every function here is pure: it only reads the habits it is given and returns a new result, without changing any habit
 or touching the database.

The functions are built from map, filter, reduce, sorted, max and generator expressions instead of loops that modify
 variables.
"""

from datetime import date, datetime, timedelta
from functools import reduce
from itertools import count, takewhile
from typing import List, Optional, Tuple

from habit_tracker.habit import Habit


def habit_names(habits: List[Habit]) -> List[str]:
    """This returns the names of all tracked habits in alphabetical order."""
    return sorted(map(lambda habit: habit.name, habits))


def habits_with_periodicity(habits: List[Habit], periodicity: str) -> List[str]:
    """This returns the names of all habits with the given periodicity, alphabetically."""
    wanted = periodicity.strip().lower()
    return habit_names(list(filter(lambda habit: habit.periodicity == wanted, habits)))


def _period_length(habit: Habit) -> timedelta:
    """This returns the length of one period of the habit: one day or one week."""
    start = habit.period_start(habit.created_at)
    return habit.next_period_start(start) - start


def _completed_periods(habit: Habit) -> List[date]:
    """This returns the start of every period with at least one check-off, oldest first."""
    return sorted(set(map(habit.period_start, habit.completions)))


def longest_streak(habit: Habit) -> int:
    """This returns the longest run of consecutive completed periods of a habit."""
    step = _period_length(habit)

    def extend(state: Tuple[int, int, Optional[date]], period: date):
        # state = (best run so far, current run, previous period)
        best, run, previous = state
        run = run + 1 if previous is not None and period - previous == step else 1
        return max(best, run), run, period

    best, _, _ = reduce(extend, _completed_periods(habit), (0, 0, None))
    return best


def current_streak(habit: Habit, now: Optional[datetime] = None) -> int:
    """This returns the number of consecutive completed periods up to now.

    If the current period is not completed yet, counting starts at the previous period, because the current one can
     still be completed.
    """
    now = now or datetime.now()
    step = _period_length(habit)
    done = set(_completed_periods(habit))
    current = habit.period_start(now)
    start = current if current in done else current - step
    periods_back = (start - step * offset for offset in count())
    return sum(1 for _ in takewhile(lambda period: period in done, periods_back))


def longest_streak_overall(habits: List[Habit]) -> Tuple[Optional[str], int]:
    """This returns the name and length of the longest streak across all habits.

    Returns ``(None, 0)`` if there are no habits.
    """
    if not habits:
        return None, 0
    best = max(habits, key=longest_streak)
    return best.name, longest_streak(best)


def longest_streak_for(habits: List[Habit], name: str) -> int:
    """This returns the longest streak of the habit with the given name.

    Raises:
        KeyError: If no habit with that name exists.
    """
    matches = [habit for habit in habits if habit.name == name]
    if not matches:
        raise KeyError("No habit named '{}' exists.".format(name))
    return longest_streak(matches[0])


def missed_periods(habit: Habit, start: date, end: date) -> int:
    """This returns how many periods between ``start`` and ``end`` were missed.

    A period counts if it starts on or after ``start`` (or after the habit was created) and before ``end``.
    """
    step = _period_length(habit)
    # First whole period that starts on or after ``start``.
    first = habit.period_start(datetime.combine(start, datetime.min.time()))
    if first < start:
        first += step
    first = max(first, habit.period_start(habit.created_at))
    periods = takewhile(lambda period: period < end,
                        (first + step * offset for offset in count()))
    done = set(_completed_periods(habit))
    return sum(1 for period in periods if period not in done)


def struggled_habits(habits: List[Habit], start: date, end: date) -> List[Tuple[str, int]]:
    """This returns the habits with missed periods in a time span, most missed first.

    Example: use the first day of last month and the first day of this month to answer
     "Which habits did I struggle with most last month?".

    Returns:
        A list of ``(name, missed periods)`` pairs; habits that were never missed are left out.
    """
    results = map(lambda habit: (habit.name, missed_periods(habit, start, end)), habits)
    struggled = filter(lambda result: result[1] > 0, results)
    return sorted(struggled, key=lambda result: (-result[1], result[0]))


