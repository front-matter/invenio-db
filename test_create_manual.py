#!/usr/bin/env python
"""Manual test for create command logic."""

from tests.conftest import create_app, _database
from invenio_db import InvenioDB
from invenio_db.cli import db as db_cmd

app = create_app()
db = _database()
InvenioDB(app, entry_point_group=False, db=db)

with app.app_context():
    runner = app.test_cli_runner()

    # Test 1: First create should succeed
    result = runner.invoke(db_cmd, ["init"])
    print("1. INIT:", result.exit_code, "OK" if result.exit_code == 0 else "FAIL")

    result = runner.invoke(db_cmd, ["create", "-v"])
    print(
        "2. FIRST CREATE:", result.exit_code, "OK" if result.exit_code == 0 else "FAIL"
    )
    print(
        '   Output contains "Creating all tables":',
        "Creating all tables" in result.output,
    )
    print(
        '   Output contains "Created all tables":',
        "Created all tables" in result.output,
    )

    # Test 2: Second create should skip
    result = runner.invoke(db_cmd, ["create", "-v"])
    print(
        "3. SECOND CREATE:", result.exit_code, "OK" if result.exit_code == 0 else "FAIL"
    )
    print(
        '   Output contains "Alembic version table already exists":',
        "Alembic version table already exists" in result.output,
    )

    # Clean up
    result = runner.invoke(db_cmd, ["destroy", "--yes-i-know"])
    print("4. DESTROY:", result.exit_code, "OK" if result.exit_code == 0 else "FAIL")
