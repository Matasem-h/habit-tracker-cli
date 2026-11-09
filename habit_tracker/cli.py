"""This file contains a command-line interface that is built with click.

This layer only handles user input and output. It passes the work on to the Habit class, the storage layer, and
the analytics module, meaning that a different interface could later reuse those modules as-is.
"""

from datetime import date, datetime, timedelta

import click

from habit_tracker import analytics
from habit_tracker.fixtures import load_predefined_habits
from habit_tracker.habit import PERIODICITIES, Habit
from habit_tracker.storage import DEFAULT_DB_PATH, HabitStorage

PERIODICITY_CHOICE = click.Choice(PERIODICITIES, case_sensitive=False)


@click.group()
@click.option("--db", default=DEFAULT_DB_PATH, show_default=True,
              help="Path to the database file.")
@click.pass_context
def cli(ctx: click.Context, db: str) -> None:
    """Habit Tracker: Create, check off, and analyze your habits."""
    ctx.obj = ctx.with_resource(HabitStorage(db))


@cli.command()
@click.argument("name")
@click.option("-d", "--description", prompt="Task description",
              help="What the task is, e.g. 'Walk for 30 minutes'.")
@click.option("-p", "--periodicity", type=PERIODICITY_CHOICE, prompt=True,
              help="How often the task must be done.")
@click.pass_obj
def add(storage: HabitStorage, name: str, description: str, periodicity: str) -> None:
    """Create a new habit called NAME."""
    try:
        storage.add_habit(Habit(name, description, periodicity))
    except ValueError as error:
        raise click.ClickException(str(error))
    click.echo("Created {} habit '{}'.".format(periodicity.lower(), name))


@cli.command()
@click.argument("name")
@click.confirmation_option(prompt="Delete this habit and all its check-offs?")
@click.pass_obj
def delete(storage: HabitStorage, name: str) -> None:
    """Delete the habit called NAME."""
    try:
        storage.delete_habit(name)
    except KeyError as error:
        raise click.ClickException(error.args[0])
    click.echo("Deleted habit '{}'.".format(name))


@cli.command()
@click.argument("name")
@click.pass_obj
def complete(storage: HabitStorage, name: str) -> None:
    """Check off the habit called NAME for the current period."""
    habit = _get_habit(storage, name)
    now = datetime.now()
    if habit.is_completed_in_period(now):
        click.echo("'{}' is already done for this {}.".format(name, _period_word(habit)))
        return
    storage.add_completion(name, habit.complete(now))
    habit = _get_habit(storage, name)
    click.echo("Checked off '{}'. Current streak: {}.".format(
        name, _streak_text(habit, analytics.current_streak(habit))))


@cli.command(name="list")
@click.option("-p", "--periodicity", type=PERIODICITY_CHOICE,
              help="Only show habits with this periodicity.")
@click.pass_obj
def list_habits(storage: HabitStorage, periodicity: str) -> None:
    """List all habits and their status in the current period."""
    habits = storage.get_all_habits()
    if periodicity:
        wanted = set(analytics.habits_with_periodicity(habits, periodicity))
        habits = [habit for habit in habits if habit.name in wanted]
    if not habits:
        click.echo("No habits found. Create one with 'add' or load examples with 'load-examples'.")
        return

    now = datetime.now()
    click.echo("{:<20} {:<8} {:<10} {}".format("Habit", "Period", "Streak", "This period"))
    for habit in habits:
        click.echo("{:<20} {:<8} {:<10} {}".format(
            habit.name[:20],
            habit.periodicity,
            _streak_text(habit, analytics.current_streak(habit, now)),
            _status(habit, now),
        ))


@cli.command()
@click.argument("name")
@click.pass_obj
def show(storage: HabitStorage, name: str) -> None:
    """Show the details and statistics of the habit called NAME."""
    habit = _get_habit(storage, name)
    last = habit.completions[-1].strftime("%Y-%m-%d %H:%M") if habit.completions else "never"
    click.echo("Habit:          {}".format(habit.name))
    click.echo("Task:           {}".format(habit.description))
    click.echo("Periodicity:    {}".format(habit.periodicity))
    click.echo("Created:        {}".format(habit.created_at.strftime("%Y-%m-%d %H:%M")))
    click.echo("Check-offs:     {}".format(len(habit.completions)))
    click.echo("Last check-off: {}".format(last))
    click.echo("Current streak: {}".format(
        _streak_text(habit, analytics.current_streak(habit))))
    click.echo("Longest streak: {}".format(
        _streak_text(habit, analytics.longest_streak(habit))))


@cli.command()
@click.argument("name", required=False)
@click.pass_obj
def streak(storage: HabitStorage, name: str) -> None:
    """Show the longest streak of all habits, or of the habit called NAME."""
    habits = storage.get_all_habits()
    if name:
        habit = _get_habit(storage, name)
        click.echo("Longest streak of '{}': {}.".format(
            name, _streak_text(habit, analytics.longest_streak_for(habits, name))))
        return

    best_name, length = analytics.longest_streak_overall(habits)
    if best_name is None:
        click.echo("No habits found.")
        return
    habit = _get_habit(storage, best_name)
    click.echo("Longest streak overall: '{}' with {}.".format(
        best_name, _streak_text(habit, length)))


@cli.command()
@click.option("-m", "--month", metavar="YYYY-MM",
              help="Month to analyse. Defaults to last month.")
@click.pass_obj
def struggled(storage: HabitStorage, month: str) -> None:
    """Show which habits were missed most often in a month."""
    start, end = _month_range(month)
    results = analytics.struggled_habits(storage.get_all_habits(), start, end)
    label = start.strftime("%B %Y")
    if not results:
        click.echo("No missed periods in {}. Well done!".format(label))
        return
    click.echo("Habits you struggled with in {}:".format(label))
    for habit_name, missed in results:
        click.echo("  {:<20} missed {} time{}".format(
            habit_name, missed, "" if missed == 1 else "s"))


@cli.command(name="load-examples")
@click.pass_obj
def load_examples(storage: HabitStorage) -> None:
    """Load the five predefined habits with four weeks of example data."""
    added = load_predefined_habits(storage)
    click.echo("Loaded {} example habit{}.".format(added, "" if added == 1 else "s"))


def _get_habit(storage: HabitStorage, name: str) -> Habit:
    """Return the habit called ``name`` or stop with a readable error."""
    habit = storage.get_habit(name)
    if habit is None:
        raise click.ClickException("No habit named '{}' exists.".format(name))
    return habit


def _period_word(habit: Habit) -> str:
    """Return 'day' or 'week' depending on the periodicity."""
    return "week" if habit.periodicity == "weekly" else "day"


def _streak_text(habit: Habit, length: int) -> str:
    """Format a streak, e.g. '3 days' or '1 week'."""
    return "{} {}{}".format(length, _period_word(habit), "" if length == 1 else "s")


def _status(habit: Habit, now: datetime) -> str:
    """Describe the habit's state in the current period."""
    if habit.is_completed_in_period(now):
        return "done"
    if habit.is_broken(now):
        return "open (streak broken)"
    return "open"


def _month_range(month: str):
    """Return the first day of ``month`` (YYYY-MM) and of the month after it.

    If no month is given, the last month is used.
    """
    if month:
        try:
            start = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            raise click.BadParameter("use the format YYYY-MM, e.g. 2026-10",
                                     param_hint="'--month'")
    else:
        start = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1)
    return start, end


