"""Shared configuration and fixtures for pytest."""

import os

import duckdb
import pytest
from click.testing import CliRunner
from constants import TEST_DB_PATH, TEST_MIGRATIONS_DIR

from quackup.cli import cli
from quackup.config import CONFIG_FILENAME, get_migrations_dir


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up an in-memory database and test migrations directory."""

    clean_test_environment()

    # Set the environment variable for the test database path
    os.environ["DUCKDB_PATH"] = TEST_DB_PATH

    yield

    clean_test_environment()


def clean_test_environment():
    """Clean up the test environment by removing generated files and directories."""

    # Remove the migrations directory and its contents
    if os.path.exists(TEST_MIGRATIONS_DIR):
        for root, dirs, files in os.walk(TEST_MIGRATIONS_DIR, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(TEST_MIGRATIONS_DIR)

    # Remove the test database file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Remove the quackup.ini config file
    if os.path.exists(CONFIG_FILENAME):
        os.remove(CONFIG_FILENAME)


@pytest.fixture(autouse=True)
def reset_environment_before_each_test():
    """Ensure a clean environment before each test."""

    clean_test_environment()

    # Re-initialize the environment using 'quackup init'
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--migrations-dir", TEST_MIGRATIONS_DIR])
    assert (
        result.exit_code == 0
    ), f"Failed to reinitialize test environment: {result.output}"

    # Verify the correct migrations directory is being used
    assert (
        get_migrations_dir() == TEST_MIGRATIONS_DIR
    ), f"Expected '{TEST_MIGRATIONS_DIR}', got '{get_migrations_dir()}'"


@pytest.fixture
def duckdb_connection():
    """Provides a connection to an in-memory DuckDB database."""
    con = duckdb.connect(TEST_DB_PATH)
    yield con
    con.close()
