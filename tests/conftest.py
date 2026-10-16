"""Shared setup for every test. pytest reads this file automatically.

Two fixtures (a fixture is something pytest prepares for a test):

* test_database: rebuilt ONCE before all tests, in a separate database
  (val_lumiere_test), so your own database val_lumiere_alumni is never touched.
* cur: a cursor inside a transaction that is CANCELLED after each test
  (ROLLBACK). A test may add rows or break rules: the next test starts
  again from the clean test data.
"""

import subprocess
from pathlib import Path

import psycopg
import pytest

ROOT = Path(__file__).resolve().parent.parent
TEST_DB = "val_lumiere_test"


@pytest.fixture(scope="session")
def test_database():
    """Rebuild the test database once, with the same script as for real use."""
    result = subprocess.run(
        [str(ROOT / "scripts" / "reset_db.sh"), TEST_DB],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.exit(f"Could not build the test database:\n{result.stdout}\n{result.stderr}")
    return f"dbname={TEST_DB}"


@pytest.fixture
def cur(test_database):
    """A cursor in a transaction that is rolled back at the end of the test."""
    conn = psycopg.connect(test_database)
    try:
        with conn.cursor() as cursor:
            yield cursor
    finally:
        conn.rollback()  # cancel everything the test did
        conn.close()
