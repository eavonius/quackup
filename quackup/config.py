"""Configuration for quackup."""

import configparser
import os

from dotenv import load_dotenv

CONFIG_FILENAME = "quackup.ini"


def get_default_config(migrations_dir: str = "migrations") -> configparser.ConfigParser:
    """
    Create and return the default configuration for the quackup.ini file.

    Parameters
    ----------
    migrations_dir: str
        The directory migrations should be created in. Defaults to "migrations".

    Returns
    -------
    configparser.ConfigParser
        A configuration parser object with quackup.ini configuration values.
    """

    config = configparser.ConfigParser()
    config["quackup"] = {
        "db_env_var": "DUCKDB_PATH",
        "migrations_dir": migrations_dir,
    }
    return config


def save_config(config: configparser.ConfigParser):
    """
    Save the configuration to the quackup.ini file.

    Parameters
    ----------
    config: configparser.ConfigParser
        A configuration parser object with quackup.ini configuration values.
    """

    with open(CONFIG_FILENAME, "w", encoding="utf8") as f:
        config.write(f)


def get_db_path() -> str:
    """
    Retrieve the path to the duckdb database.

    Returns
    -------
    str
        The path to the duckdb database to migrate.
    """

    load_dotenv()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)

    db_env_var = config.get("quackup", "db_env_var", fallback="DUCKDB_PATH")
    db_path = os.getenv(db_env_var)

    if not db_path:
        raise ValueError(
            f"Environment variable '{db_env_var}' is not set "
            "or does not contain a valid path."
        )

    return db_path


def get_migrations_dir() -> str:
    """
    Retrieve the configured migrations directory.

    Returns
    -------
    str
        The relative directory to use for creating and running database migrations.
    """
    if not os.path.exists(CONFIG_FILENAME):
        raise FileNotFoundError(f"Configuration file '{CONFIG_FILENAME}' is missing.")

    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    return config.get("quackup", "migrations_dir", fallback="migrations")
