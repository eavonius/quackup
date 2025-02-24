"""Builds T-SQL content for up/down migration files."""

from datetime import datetime


def build_up_migration(name: str) -> str:
    """
    Builds a migration for up.sql with transactional support.

    Parameters
    ----------
    name: str
        The name of the new migration.

    Returns
    -------
    str
        The contents of the new migration file.
    """

    return f"""\
-- Up migration for: "{name}"
-- Created on {datetime.now()}

BEGIN TRANSACTION;

-- Your migration logic here
-- Example: ALTER TABLE users ADD COLUMN age INTEGER;

COMMIT;
"""


def build_down_migration(name: str) -> str:
    """
    Builds a migration for down.sql with transactional support.

    Parameters
    ----------
    name: str
        The name of the new migration.

    Returns
    -------
    str
        The contents of the new migration file.
    """

    return f"""\
-- Down migration for: "{name}"
-- Created on {datetime.now()}

BEGIN TRANSACTION;

-- Your rollback logic here
-- Example: ALTER TABLE users DROP COLUMN age;

COMMIT;
"""
