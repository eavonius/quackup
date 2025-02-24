"""Tests the quackup/migrator.py module"""

import os
import re

import duckdb
import pytest
from constants import TEST_DB_PATH

from quackup.config import CONFIG_FILENAME, get_migrations_dir
from quackup.migrator import generate_migration, run_migrations


def test_generate_migration():
    """Test the generation of a new migration."""

    migration_name = "create_test_table"
    generate_migration(migration_name)
    migrations_dir = get_migrations_dir()

    assert (
        migrations_dir == "test_migrations"
    ), f"Expected 'test_migrations', got '{migrations_dir}'"

    print(f"LISTING CONTENTS OF {migrations_dir}")

    # Get only the newly generated migration folder
    migration_folders = os.listdir(migrations_dir)
    assert len(migration_folders) == 1  # Ensure only one migration exists

    folder_name = migration_folders[0]
    expected_pattern = (
        r"^\d{4}_\d{2}_\d{2}_\d{4}-[a-f0-9]{8}_" + re.escape(migration_name) + r"$"
    )
    assert re.match(expected_pattern, folder_name)

    assert migration_name in folder_name
    assert os.path.exists(os.path.join(migrations_dir, folder_name, "up.sql"))
    assert os.path.exists(os.path.join(migrations_dir, folder_name, "down.sql"))


def test_run_migrations_up(duckdb_connection):
    """Test applying an up migration."""

    generate_migration("create_users_table")

    print(f"Migrations dir: {get_migrations_dir()}")

    migration_folder = os.listdir(get_migrations_dir())[0]

    up_sql_path = os.path.join(get_migrations_dir(), migration_folder, "up.sql")
    with open(up_sql_path, "w") as f:
        f.write("CREATE TABLE users (id INTEGER, name TEXT);")

    run_migrations(dry_run=False, direction="up")

    result = duckdb_connection.execute("SELECT * FROM users").fetchall()
    assert result == []


def test_run_migrations_down(duckdb_connection):
    """Test rolling back the latest migration."""

    run_migrations(dry_run=False, direction="down", rollback_count=1)

    try:
        duckdb_connection.execute("SELECT * FROM users").fetchall()
    except Exception as e:
        assert "Table with name users does not exist" in str(e)


def test_dry_run_does_not_modify_database():
    """Test that running migrations in dry-run mode does not change the database."""

    generate_migration("create_users_table")
    migration_folder = os.listdir(get_migrations_dir())[0]

    up_sql_path = os.path.join(get_migrations_dir(), migration_folder, "up.sql")
    with open(up_sql_path, "w") as f:
        f.write("CREATE TABLE users (id INTEGER, name TEXT);")

    # Run in dry-run mode
    run_migrations(dry_run=True, direction="up")

    # Check that the table does not exist
    connection = duckdb.connect(TEST_DB_PATH)
    with pytest.raises(duckdb.CatalogException):
        connection.execute("SELECT * FROM users").fetchall()
    connection.close()


def test_invalid_migration_sql_partial_rollback():
    """Test handling of invalid SQL during migration execution."""

    generate_migration("create_invalid_table")
    migration_folder = os.listdir(get_migrations_dir())[0]

    up_sql_path = os.path.join(get_migrations_dir(), migration_folder, "up.sql")
    with open(up_sql_path, "w") as f:
        f.write("CREATE TABLE valid_table (id INTEGER);\nINVALID SQL SYNTAX;")

    # Attempt to run the migration, expecting a failure
    with pytest.raises(
        Exception, match=r"Parser Error: syntax error at or near \"INVALID\""
    ):
        run_migrations(dry_run=False, direction="up")

    # Verify that no partial changes were applied
    connection = duckdb.connect(TEST_DB_PATH)
    with pytest.raises(duckdb.CatalogException):
        connection.execute("SELECT * FROM valid_table").fetchall()
    connection.close()


def test_missing_migrations_directory():
    """Test behavior when the migrations directory is missing."""

    migrations_dir = get_migrations_dir()

    # Remove the migrations directory if it exists
    if os.path.exists(migrations_dir):
        for root, dirs, files in os.walk(migrations_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(migrations_dir)

    # Attempt to run migrations with no migrations directory
    with pytest.raises(FileNotFoundError, match="Migrations directory"):
        run_migrations(dry_run=False, direction="up")


def test_missing_config_file():
    """Test behavior when the quackup.ini config file is missing."""

    if os.path.exists(CONFIG_FILENAME):
        os.remove(CONFIG_FILENAME)

    with pytest.raises(FileNotFoundError, match="Configuration file"):
        run_migrations(dry_run=False, direction="up")


def test_repeated_migrations_up_and_down():
    """Test running up and down migrations repeatedly without errors."""
    generate_migration("create_repeated_table")
    migration_folder = os.listdir(get_migrations_dir())[0]

    up_sql_path = os.path.join(get_migrations_dir(), migration_folder, "up.sql")
    down_sql_path = os.path.join(get_migrations_dir(), migration_folder, "down.sql")
    with open(up_sql_path, "w") as f:
        f.write("CREATE TABLE repeated_table (id INTEGER);")
    with open(down_sql_path, "w") as f:
        f.write("DROP TABLE IF EXISTS repeated_table;")

    # Apply the migration twice (should not error on second run)
    run_migrations(dry_run=False, direction="up")
    run_migrations(dry_run=False, direction="up")

    # Rollback the migration twice (should not error on second run)
    run_migrations(dry_run=False, direction="down")
    run_migrations(dry_run=False, direction="down")


def test_missing_duckdb_path_env_var(monkeypatch):
    """Test behavior when the DUCKDB_PATH environment variable is not set."""
    monkeypatch.delenv("DUCKDB_PATH", raising=False)

    with pytest.raises(
        ValueError, match="Environment variable 'DUCKDB_PATH' is not set"
    ):
        run_migrations(dry_run=False, direction="up")


def test_incorrect_duckdb_path_env_var(monkeypatch):
    """Test behavior when the DUCKDB_PATH environment variable is incorrect."""
    monkeypatch.setenv("DUCKDB_PATH", "invalid_path/invalid.duckdb")

    with pytest.raises(Exception, match="Cannot open file"):
        run_migrations(dry_run=False, direction="up")
