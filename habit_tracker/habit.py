"""The habit class: the object-oriented core of the habit tracker."""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

DAILY = "daily"
WEEKLY = "weekly"
PERIODICITIES = (DAILY, WEEKLY)

class Habit:
    """A single habit with a task description and a periodicity.

    Completions are stored in a private, sorted list.
    Outside code can read them using the ''completions'' property but can only add new ones using ''complete()''
    , which means that the list cannot be accidentally changed.

    Attributes:
        name: Unique, human-readable name, e.g. "Swimming".
        description: What the task is, e.g., "Swimming for 30 minutes".
        periodicity: Either "daily" or "weekly".
        created_at: Date and time the habit was created.
    """

    def __init__(
            self,
            name: str,
            description: str,
            periodicity: str,
            created_at: Optional[datetime] = None,
            completions: Optional[List[datetime]] = None,
    ):
        """Create a habit

        Args:
            name: Unique name, must not be empty.
            description: Task specification.
            periodicity: Case-insensitive "daily" or "weekly".
            created_at: Creation time, its default is "Now".
            completions: Existing check-off times, its default is "Now".

        Raises:
            ValueError: If the name is empty or the periodicity is unknown.
        """
        if not name or not name.strip():
            raise ValueError("Habit name must not be empty.")

        periodicity = periodicity.strip().lower()
        if periodicity not in PERIODICITIES:
            raise ValueError(
                "Periodicity must be one of: {}.".format(", ".join(PERIODICITIES))
            )

        self.name = name.strip()
        self.description: description.strip()
        self.periodicity: periodicity.strip()
        self.created_at: created_at.strip()

        # Private by convention; only complete() adds to it.
        self._completions = sorted(completions or [])

    @property
    def completions(self) -> Tuple[datetime, ...]:
        """All check-off times, oldest first, as a read-only tuple."""
        # A tuple copy stops callers from editing the private list.
        return tuple(self._completions)

    def complete(self, when: Optional[datetime] = None) -> datetime:
        """Check off the habit at the given time.

        Args:
            when: Time of the check-off, with its default being "Now".

        Returns:
            the recorded check-off time.

        Raises:
            ValueError: If the check-off lies before the habit was created.
        """
        when = when or datetime.now()
        if when < self.created_at:
            raise ValueError("A habit cannot be completed before it was created.")
        self._completions.append(when)
        self._completions.sort()
        return when

    def period_start(self, moment: datetime) -> date:
        """Return the first dat of the period that contains ''moment''.

        Daily habits use the calendar day.
        Weekly habits use the calendar week from Monday to Sunday, which means that the Monday of that week is returned.
        """
        day = moment.date()
        if self.periodicity == WEEKLY:
            # weekday() is 0 for Monday, meaning that this always lands on Monday.
            return day - timedelta(days=day.weekday())
        return day

    def next_period_start(self, start: date) -> date:
        """Return the first day of the period that contains ''moment''.

        Daily habits use the calendar day. Weekly habits use the calendar week from Monday to Sunday
        , which means that the Monday of that week is returned.
        """
        day = moment.date()
        if self.periodicity == WEEKLY:
            # weekday() is 0 for Monday, which means that this always lands on Monday.
            return day - timedelta(days=day.weekday())
        return day

    def next_period_start(self, start: date) -> date:
        """Return the first day of the period after the one starting at ''start''."""
        return start + timedelta(days=7 if self.periodicity == WEEKLY else 1)

    def is_completed_in_period(self, moment: datetime) -> bool:
        """Retrun True if the habit was checked off in the period of ''moment''."""
        target = self.period_start(moment)
        return any(self.period_start(done) == target for done in self._completions)

    def is_broken(self, now: Optional[datetime] = None) -> bool:
        """Return True if the most recently finished period was missed.

        The current period is still running, so it cannot be missed yet.
        A habit created during the current period has no finished period and is therefore never broken.

        Args:
            now: References time, with its default being "Now".
        """
        now = now or datetime.now()
        current = self.period_start(now)
        created = self.period_start(self.created_at)
        if created >= current:
            return False

        # Step back one period length to reach the last finished period.
        previous = current - (self.next_period_start(current) - current)
        return not any(self.period_start(done) == previous for done in self._completions)

    def __repr__(self) -> str:
        """Return a readable representation for debugging."""
        return "Habit(name{!r}, periodicity={!r}, completions{})".format(
            self.name, self.periodicity, len(self._completions)
        )


