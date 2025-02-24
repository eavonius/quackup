"""Migrator functions for quackup."""

import os
from datetime import datetime
from uuid import uuid4

import duckdb

from .config import CONFIG_FILENAME, get_db_path, get_migrations_dir
from .migration_builder import build_down_migration, build_up_migration


def get_db_connection() -> duckdb.DuckDBPyConnection:
    """
    Retrieves a connection to the DuckDB database.

    Returns
    -------
    duckdb.DuckDBPyConnection
        A connection to the duckdb database to find migrations in.
    """

    db_path = get_db_path()
    return duckdb.connect(db_path)


def initialize_migrations_table(connection: duckdb.DuckDBPyConnection):
    """
    Creates the migration tracking table in the database.

    Parameters
    ----------
    connection: duckdb.DuckDBPyConnection
        A connection to the duckdb database to find migrations in.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS duckdb_migrations (
            name TEXT PRIMARY KEY,
            applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'up'
        )
    """
    )


def get_applied_migrations(connection: duckdb.DuckDBPyConnection) -> dict:
    """
    Retrieves a list of applied migrations from the database with status.

    Parameters
    ----------
    connection: duckdb.DuckDBPyConnection
        A connection to the duckdb database to find migrations in.

    Returns
    -------
    dict
        A dictionary containing the name and status of migrations that were applied.
    """

    results = connection.execute(
        "SELECT name, status FROM duckdb_migrations"
    ).fetchall()

    return {row[0]: row[1] for row in results}


def apply_migration(
    connection: duckdb.DuckDBPyConnection, filename: str, sql: str, status: str = "up"
):
    """
    Executes a migration and records it in the database.

    Parameters
    ----------
    connection: duckdb.DuckDBPyConnection
        A connection to the duckdb database to apply the migration to.
    filename: str
        The filename of the migration to apply.
    sql: str
        The SQL statement to execute contained in the migration being applied.
    status: str
        Whether to set the status of the migration to an "up" or "down" migration.
        Defaults to "up".
    """

    print(f"Applying migration: {filename} ({status})")

    connection.execute(sql)
    connection.execute(
        """
        INSERT INTO duckdb_migrations (name, applied, status)
        VALUES (?, CURRENT_TIMESTAMP, ?)
        ON CONFLICT (name) DO UPDATE SET status = ?
    """,
        [filename, status, status],
    )


def run_migrations(
    dry_run: bool = False, direction: str = "up", rollback_count: int = 1
):
    """
    Executes all pending migrations in the correct order.

    Parameters
    ----------
    dry_run: bool
        Preview the changes but don't apply them. Defaults to False.
    direction: str
        Whether to run an "up" or "down" migration. Defaults to "up".
    rollback_count: int
        The number of migrations to rollback if running "down". Defaults to 1.
    """

    migrations_dir = get_migrations_dir()

    # Ensure the migrations directory exists
    if not os.path.exists(migrations_dir):
        raise FileNotFoundError(
            f"Migrations directory '{migrations_dir}' does not exist."
        )

    # Ensure the config file exists
    if not os.path.exists(CONFIG_FILENAME):
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILENAME}' is missing.")

    connection = get_db_connection()

    try:
        initialize_migrations_table(connection)

        applied_migrations = get_applied_migrations(connection)

        # Sort migrations by applied timestamp, newest first
        migration_folders = sorted(os.listdir(migrations_dir), reverse=True)

        migrations_to_process = []

        for folder_name in migration_folders:
            if os.path.isdir(os.path.join(migrations_dir, folder_name)):
                status = applied_migrations.get(folder_name, "down")

                if (direction == "up" and status == "down") or (
                    direction == "down" and status == "up"
                ):
                    migrations_to_process.append(folder_name)

                    if (
                        direction == "down"
                        and len(migrations_to_process) >= rollback_count
                    ):
                        break  # Stop after reaching the rollback count

        if direction == "down" and not migrations_to_process:
            print("No migrations found to rollback.")
            return

        for folder_name in migrations_to_process:
            sql_file = "up.sql" if direction == "up" else "down.sql"

            file_path = os.path.join(migrations_dir, folder_name, sql_file)

            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    migration_sql = f.read()

                if dry_run:
                    print(
                        f"[DRY RUN] Would apply {direction} " "migration: {folder_name}"
                    )
                else:
                    apply_migration(connection, folder_name, migration_sql, direction)
            else:
                print(f"No {sql_file} found for " "migration {folder_name}. Skipping.")

        if not dry_run:
            print("All migrations applied successfully.")

    finally:
        connection.close()


def generate_migration(name: str):
    """
    Generates a new migration folder with up.sql and down.sql files.

    Parameters
    ----------
    name: str
        The base name of the migration. Will have spaces replaced with underscores
        and be prefixed with a timestamp and unique id to attempt to prevent duplicates.
    """
    migrations_dir = get_migrations_dir()

    os.makedirs(migrations_dir, exist_ok=True)

    sanitized_name = name.strip().replace(" ", "_").lower()

    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")

    unique_id = str(uuid4())[:8]  # Similar to Alembic revision IDs

    folder_name = f"{timestamp}-{unique_id}_{sanitized_name}"
    folder_path = os.path.join(get_migrations_dir(), folder_name)

    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "up.sql"), "w") as f:
        f.write(build_up_migration(name))

    with open(os.path.join(folder_path, "down.sql"), "w") as f:
        f.write(build_down_migration(name))

    print(f"Created new migration folder: {folder_path}")


def status():
    """Shows the status of all migrations."""

    migrations_dir = get_migrations_dir()

    connection = get_db_connection()

    try:
        initialize_migrations_table(connection)

        applied_migrations = get_applied_migrations(connection)

        print(f'{"Migration":<60} {"Status":<10}')

        print("-" * 70)

        for folder_name in sorted(os.listdir(migrations_dir)):
            if os.path.isdir(os.path.join(migrations_dir, folder_name)):
                status = applied_migrations.get(folder_name, "down")
                print(f"{folder_name:<60} {status:<10}")
    finally:
        connection.close()
