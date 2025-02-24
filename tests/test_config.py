"""Tests the quackup/config.py module"""

import os

from constants import TEST_DB_PATH

from quackup.config import get_db_path, get_migrations_dir


def test_get_db_path():
    """Test that the correct DuckDB path is retrieved."""

    # Ensure the environment variable is set correctly
    os.environ["DUCKDB_PATH"] = TEST_DB_PATH

    db_path = get_db_path()
    assert db_path == TEST_DB_PATH


def test_get_migrations_dir():
    """Test that the configured migrations directory is used."""
    migrations_dir = get_migrations_dir()
    assert migrations_dir == "test_migrations"
