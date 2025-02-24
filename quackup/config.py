"""Configuration for quackup."""

import configparser
import os

from dotenv import load_dotenv

DEFAULT_CONFIG = """
[quackup]
db_env_var = DUCKDB_PATH
"""


def get_db_path() -> str:
    """Retrieve the path to the duckdb database."""

    # Load .env file if present
    load_dotenv()

    # Load configuration from quackup.ini
    CONFIG_FILE = "quackup.ini"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    # Get the environment variable name for the DuckDB file path
    db_env_var = config.get("quackup", "db_env_var", fallback="DUCKDB_PATH")

    # Get the actual DuckDB file path from the environment
    db_path = os.getenv(db_env_var)

    if not db_path:
        raise ValueError(
            f"Environment variable '{db_env_var}' is not set "
            "or does not contain a valid path."
        )

    return db_path
