"""This file contains tests for the command-line interface, using click's test runner."""

import pytest
from click.testing import CliRunner

from habit_tracker.cli import cli


@pytest.fixture
def run(tmp_path):
    """Return a function that runs a CLI command against a temporary database."""
    runner = CliRunner()
    db = str(tmp_path / "test.db")

    def invoke(*args, **kwargs):
        return runner.invoke(cli, ["--db", db] + list(args), **kwargs)

    return invoke


def test_add_and_list(run):
    result = run("add", "Reading", "-d", "Read 10 pages", "-p", "daily")
    assert result.exit_code == 0
    assert "Created daily habit 'Reading'" in result.output
    assert "Reading" in run("list").output


def test_add_prompts_for_missing_options(run):
    result = run("add", "Reading", input="Read 10 pages\nweekly\n")
    assert result.exit_code == 0
    assert "Created weekly habit 'Reading'" in result.output


def test_add_duplicate_shows_error(run):
    run("add", "Reading", "-d", "Read 10 pages", "-p", "daily")
    result = run("add", "Reading", "-d", "Read 10 pages", "-p", "daily")
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_add_rejects_unknown_periodicity(run):
    result = run("add", "Reading", "-d", "Read 10 pages", "-p", "monthly")
    assert result.exit_code != 0


def test_complete_checks_off_once_per_period(run):
    run("add", "Reading", "-d", "Read 10 pages", "-p", "daily")
    first = run("complete", "Reading")
    assert "Checked off 'Reading'. Current streak: 1 day." in first.output
    second = run("complete", "Reading")
    assert "already done for this day" in second.output


def test_complete_unknown_habit_shows_error(run):
    result = run("complete", "Nothing")
    assert result.exit_code != 0
    assert "No habit named 'Nothing'" in result.output


def test_delete_asks_for_confirmation(run):
    run("add", "Reading", "-d", "Read 10 pages", "-p", "daily")
    run("delete", "Reading", input="n\n")
    assert "Reading" in run("list").output
    run("delete", "Reading", "--yes")
    assert "No habits found" in run("list").output


def test_list_filters_by_periodicity(run):
    run("load-examples")
    output = run("list", "-p", "weekly").output
    assert "Clean apartment" in output
    assert "Walking" not in output


def test_load_examples_only_once(run):
    assert "Loaded 5 example habits." in run("load-examples").output
    assert "Loaded 0 example habits." in run("load-examples").output


def test_streak_overall_and_per_habit(run):
    run("load-examples")
    assert "'Drink water' with 28 days" in run("streak").output
    assert "'Call family': 2 weeks" in run("streak", "Call family").output


def test_struggled_in_october(run):
    run("load-examples")
    output = run("struggled", "-m", "2026-10").output
    assert "October 2026" in output
    assert output.index("Walking") < output.index("Study") < output.index("Call family")


def test_struggled_rejects_bad_month(run):
    result = run("struggled", "-m", "October")
    assert result.exit_code != 0
    assert "YYYY-MM" in result.output


def test_show_displays_details(run):
    run("load-examples")
    output = run("show", "Walking").output
    assert "Walk for 30 minutes" in output
    assert "Longest streak: 12 days" in output


