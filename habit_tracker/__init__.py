"""Habit Tracker is a command-line habit tracking backend.

The package is split into one module per responsibility:

* ``habit``     - the Habit class (object-oriented domain model).
* ``storage``   - SQLite persistence layer.
* ``analytics`` - pure functions for analysing habits (functional programming).
* ``fixtures``  - five predefined habits with four weeks of example data.
* ``cli``       - the click-based command-line interface.
"""


