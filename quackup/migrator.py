"""Migrator functions for quackup."""

import os
from datetime import datetime
from uuid import uuid4

import duckdb

from .config import get_db_path

MIGRATIONS_PATH = "migrations"
DB_PATH = get_db_path()


def initialize_migrations_table(con):
    """Ensure the migration tracking table exists in DuckDB."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS duckdb_migrations (
            name TEXT PRIMARY KEY,
            applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'up'
        )
    """
    )


def get_applied_migrations(con) -> dict:
    """Retrieve the list of applied migrations from the database with status."""
    results = con.execute("SELECT name, status FROM duckdb_migrations").fetchall()
    return {row[0]: row[1] for row in results}


def apply_migration(con, filename: str, sql: str, status: str = "up"):
    """Execute a migration and record it in the database."""
    print(f"Applying migration: {filename} ({status})")
    con.execute(sql)
    con.execute(
        """
        INSERT INTO duckdb_migrations (name, applied, status) 
        VALUES (?, CURRENT_TIMESTAMP, ?) 
        ON CONFLICT (name) DO UPDATE SET status = ?
    """,
        [filename, status, status],
    )


def run_migrations(dry_run: bool = False, direction: str = "up"):
    """Execute all pending migrations in the correct order."""
    con = duckdb.connect(DB_PATH)
    initialize_migrations_table(con)
    applied_migrations = get_applied_migrations(con)

    for folder_name in sorted(os.listdir(MIGRATIONS_PATH)):
        if os.path.isdir(os.path.join(MIGRATIONS_PATH, folder_name)):
            status = applied_migrations.get(folder_name, "down")
            if (direction == "up" and status == "down") or (
                direction == "down" and status == "up"
            ):
                sql_file = "up.sql" if direction == "up" else "down.sql"
                file_path = os.path.join(MIGRATIONS_PATH, folder_name, sql_file)
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        migration_sql = f.read()
                    if dry_run:
                        print(
                            f"[DRY RUN] Would apply {direction} "
                            "migration: {folder_name}"
                        )
                    else:
                        apply_migration(con, folder_name, migration_sql, direction)
                else:
                    print(f"No {sql_file} found for migration {folder_name}. Skipping.")

    con.close()
    if not dry_run:
        print("All migrations applied successfully.")


def generate_migration(name: str):
    """Generate a new migration folder with up.sql and down.sql files."""
    sanitized_name = name.strip().replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    unique_id = str(uuid4())[:8]  # Similar to Alembic revision IDs
    folder_name = f"{timestamp}-{unique_id}_{sanitized_name}"
    folder_path = os.path.join(MIGRATIONS_PATH, folder_name)

    os.makedirs(folder_path, exist_ok=True)

    with open(os.path.join(folder_path, "up.sql"), "w") as f:
        f.write(f"-- Up migration: {name}\n-- Created on {datetime.now()}\n\n")

    with open(os.path.join(folder_path, "down.sql"), "w") as f:
        f.write(f"-- Down migration: {name}\n-- Created on {datetime.now()}\n\n")

    print(f"Created new migration folder: {folder_path}")


def status():
    """Show the status of all migrations."""
    con = duckdb.connect(DB_PATH)
    initialize_migrations_table(con)
    applied_migrations = get_applied_migrations(con)

    print(f'{"Migration":<60} {"Status":<10}')
    print("-" * 70)
    for folder_name in sorted(os.listdir(MIGRATIONS_PATH)):
        if os.path.isdir(os.path.join(MIGRATIONS_PATH, folder_name)):
            status = applied_migrations.get(folder_name, "down")
            print(f"{folder_name:<60} {status:<10}")

    con.close()
