import os
import click
from .config import DEFAULT_CONFIG
from .migrator import run_migrations, generate_migration, status

@click.group()
def cli():
    '''DuckDB Migration Tool'''
    pass

@cli.command()
@click.option('--dry-run', is_flag=True, help='Run migrations without applying changes.')
def up(dry_run):
    '''Apply all pending migrations.'''
    run_migrations(dry_run=dry_run, direction='up')

@cli.command()
@click.option('--dry-run', is_flag=True, help='Run rollback migrations without applying changes.')
def down(dry_run):
    '''Rollback all applied migrations in reverse order.'''
    run_migrations(dry_run=dry_run, direction='down')

@cli.command()
@click.argument('name')
def create(name):
    '''Create a new migration with up and down scripts.'''
    generate_migration(name)

@cli.command()
def status_cmd():
    '''Show the status of all migrations.'''
    status()

@cli.command()
def init():
    """Initialize QuackUp configuration and migrations directory."""
    # Create the quackup.ini file if it doesn't exist
    config_file = 'quackup.ini'
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write(DEFAULT_CONFIG.strip())
        click.echo(f'Created {config_file} with default settings.')
    else:
        click.echo(f'{config_file} already exists. Skipping creation.')

    # Create the migrations directory if it doesn't exist
    migrations_dir = 'migrations'
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)
        click.echo(f'Created {migrations_dir} directory.')
    else:
        click.echo(f'{migrations_dir} directory already exists. Skipping creation.')

if __name__ == '__main__':
    cli()
