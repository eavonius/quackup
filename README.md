# quackup

quackup is a simple and powerful migration tool for [duckdb](https://duckdb.org/) databases, designed with a clean and familiar CLI interface. Inspired by tools like [alembic](https://github.com/sqlalchemy/alembic) and [flyway](https://github.com/flyway/flyway), quackup helps manage your database schema changes with **up/down migrations**, **versioning**, and **safe rollbacks**.

---

## Key features

- **Versioned migrations:** Automatically generate timestamped migrations containing raw duckdb-compatible SQL statements.
- **Up & down migrations:** Apply and rollback migrations easily using the CLI.
- **Configurable migrations directory:** Specify a custom directory for migrations if you need to use quackup alongside other migration tools in the same project.
- **Dry-run mode:** Preview what migrations will run without applying any changes using the `--dry-run` option.
- **Flexible rollbacks:** Rollback a specific number of the latest applied migrations using the `--count` option.
- **Migration status:** View which migrations are applied or pending.
- **Supports .env Files:** Easily specify the path to your duckdb database using environment variables.

---

## Installation

quackup is available on [pypi](https://pypi.org/project/quackup/) and can be installed using pip:

```sh
pip install quackup
```

---

## Contents

- [Project structure](#project-structure)
- [Initilization](#1-initialize-quackup)
- [Configuration](#2-configure-quackup)
- [Creating migrations](#3-create-a-new-migration)
- [Applying migrations](#4-apply-all-pending-migrations)
- [Rolling back migrations](#5-rollback-migrations)
- [Listing migration status](#6-check-migration-status)

---

## Project structure

Below is a depiction of the files contained in a typical python project using quackup. The migrations directory may be named differently if configured with a custom name.

```plaintext
.
├─ migrations/
│    ├─ 2025_02_25_1450-00123abc_create_users_table/
│    │    ├─ up.sql
│    │    └─ down.sql
│    └─ 2025_02_25_1500-00456def_add_email_to_users/
│         ├─ up.sql
│         └─ down.sql
├─ quackup.ini
└─ .env (optional)
```

---

## Usage

### 1. Initialize quackup

Before you can use quackup in your project, you need to initialize it. This creates configuration files necessary for it to work.

```sh
quackup init
```

This will create a `quackup.ini` configuration file and a `migrations` directory (if they don't already exist):

```plaintext
.
├─ quackup.ini       # Configuration file for quackup
└─ migrations/       # Directory for storing migration files
```

To specify a custom migrations directory, use the --migrations-dir option:

```sh
quackup init --migrations-dir custom_migrations
```

### 2. Configure quackup

After running `quackup init`, the `quackup.ini` file will contain:

```ini
[quackup]
db_env_var = DUCKDB_PATH
migrations_dir = migrations
```

You can then set the path to your duckdb database using a `.env` file. The name of the environment variable must match the value you set `db_env_var` to in your `quackup.ini` file.

```plaintext
# .env file
DUCKDB_PATH=/path/to/your_database.duckdb
```

When deploying your migrations into a staging or production environment for example, you'll want to set this variable's value in the system's environment (or a Docker image).

### 3. Create a new migration

```sh
quackup create "Add email to users table"
```

This will generate a timestamped migration folder inside the
configured migrations directory with `up.sql` and `down.sql` files:

```plaintext
migrations/
└─ 2025_02_25_1500-00456def_add_email_to_users/
     ├─ up.sql
     └─ down.sql
```

Place the SQL statements you want to run during a migration in the
`up.sql` file, and corresponding SQL statements you want to undo those
changes in the `down.sql` file in the same folder.

#### Transaction support

The generated up.sql and down.sql files are automatically wrapped in a duckdb
transaction, ensuring atomicity:

```sql
BEGIN TRANSACTION;

-- Your migration logic here
-- Example: ALTER TABLE users ADD COLUMN age INTEGER;

COMMIT;
```

This prevents partial application of migrations and helps maintain database integrity.

---

### 4. Apply all pending migrations

```sh
quackup up
```

If you specified a custom migrations directory during initialization,
quackup will automatically use it.

You can also dry-run to see which migrations would be applied:

```sh
quackup up --dry-run
```

---

### 5. Rollback migrations

To rollback the **latest** migration (default behavior):

```sh
quackup down
```

To rollback a specific number of recent migrations, use the `--count` option:

```sh
quackup down --count 3
```

The above example would rollback the three most recently applied migrations.

You can also preview the rollback actions without applying changes using
the dry-run mode:

```sh
quackup down --count 2 --dry-run
```

The above example would show the contents of the most recent two migrations
that would be rolled back, but will not actually apply them.

---

### 6. Check migration status

```sh
quackup status
```

Example Output:

```plaintext
Migration                                        Status
-------------------------------------------------------
2025_02_25_1450-00123abc_create_users_table      up
2025_02_25_1500-00456def_add_email_to_users      down
```

If a custom migrations directory is configured, this command
will automatically reflect that.

---

## ⚠️ Important considerations

- **Always test migrations** in a staging environment before applying them
  in production to prevent accidental data loss.
- When rolling back migrations, use the `--count` option to
  **precisely control how many migrations are undone**.
- The dry-run mode is a great way to
  **verify what quackup will execute before applying changes**.

---

## Contributing

Contributions are welcome! If you find bugs, have feature requests, or want to contribute, please [open an issue](https://github.com/eavonius/quackup/issues) or [submit a pull request](https://github.com/eavonius/quackup/pulls).

### Testing contributions

To run tests in your own fork:

1. Create a virtual environment in the `.venv` directory.

   ```sh
   py -m pip install virtualenv
   py -m virtualenv .venv
   ```

2. Enter the virtual environment.

   Run the appropriate _activate_ script depending on your shell.

   Examples:

   - Bash:
     ```bash
     source ./.venv/scripts/activate.sh
     ```
   - Windows PowerShell:
     ```powershell
     .\.venv\Scripts\Activate
     ```

3. Install test dependencies with `pip install -e .[test]`

4. Run tests with `pytest -v`

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
