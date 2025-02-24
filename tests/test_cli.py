"""Tests the quackup/cli.py module"""

import os

from click.testing import CliRunner
from constants import TEST_MIGRATIONS_DIR

from quackup.cli import cli
from quackup.config import CONFIG_FILENAME, get_migrations_dir


def test_init_command():
    """Test the quackup init CLI command."""
    runner = CliRunner()

    # Ensure the test environment is clean
    migrations_dir = get_migrations_dir()
    if os.path.exists(CONFIG_FILENAME):
        os.remove(CONFIG_FILENAME)
    if os.path.exists(migrations_dir):
        for root, dirs, files in os.walk(migrations_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(migrations_dir)

    result = runner.invoke(cli, ["init", "--migrations-dir", TEST_MIGRATIONS_DIR])
    assert result.exit_code == 0
    assert "Created test_migrations directory." in result.output
    assert "Created quackup.ini with default settings." in result.output


def test_create_migration_command():
    """Test the quackup create CLI command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "add_email_to_users"])
    assert result.exit_code == 0
    assert "Created new migration folder" in result.output
