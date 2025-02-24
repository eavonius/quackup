"""Command-line interface for quackup."""

import os

import click

from .config import CONFIG_FILENAME, get_default_config, save_config
from .migrator import generate_migration, run_migrations, status


@click.group()
def cli():
    """DuckDB Migration Tool"""


@cli.command()
@click.option(
    "--dry-run", is_flag=True, help="Run migrations without applying changes."
)
def up(dry_run):
    """
    Applies all pending migrations.

    Parameters
    ----------
    dry_run: bool
        Preview the changes but don't apply them. Defaults to False.
    """
    run_migrations(dry_run=dry_run, direction="up")


@cli.command()
@click.option(
    "--count",
    default=1,
    type=int,
    help="Number of migrations to rollback. Default is 1.",
)
@click.option(
    "--dry-run", is_flag=True, help="Preview the rollbacks without applying changes."
)
def down(count, dry_run):
    """
    Rolls back the latest applied migration in reverse order.

    Parameters
    ----------
    count: int
        The number of migrations to rollback. Defaults to 1.
    dry_run: bool
        Preview the changes but don't apply them. Defaults to False.
    """
    run_migrations(dry_run=dry_run, direction="down", rollback_count=count)


@cli.command()
@click.argument("name")
def create(name):
    """
    Creates a new migration with up and down scripts.

    Parameters
    ----------
    name: str
        The base name of the migration. Will have spaces replaced with underscores
        and be prefixed with a timestamp and unique id to attempt to prevent duplicates.
    """
    generate_migration(name)


@cli.command()
def status_cmd():
    """Shows the status of all migrations."""
    status()


@cli.command()
@click.option(
    "--migrations-dir", default="migrations", help="Directory to store migrations."
)
def init(migrations_dir):
    """
    Initializes quackup configuration and the migrations directory.

    Parameters
    ----------
    migrations_dir: str
        The directory containing migration scripts.
    """

    # Create the migrations directory if it doesn't exist
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)
        click.echo(f"Created {migrations_dir} directory.")
    else:
        click.echo(f"{migrations_dir} directory already exists. Skipping creation.")

    # Create the quackup.ini file if it doesn't exist
    if not os.path.exists(CONFIG_FILENAME):
        config = get_default_config(migrations_dir)
        save_config(config)
        click.echo(f"Created {CONFIG_FILENAME} with default settings.")
    else:
        click.echo(f"{CONFIG_FILENAME} already exists. Skipping creation.")


if __name__ == "__main__":
    cli()
