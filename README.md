# quackup 🦆

quackup is a simple and powerful migration tool for **DuckDB** databases, designed with a clean and familiar CLI interface. Inspired by tools like **Alembic** and **Flyway**, quackup helps manage your database schema changes with **up/down migrations**, **versioning**, and **safe rollbacks**.

---

## 🎯 **Key Features:**

- **Versioned Migrations:** Automatically generate **timestamped migrations** with **up/down SQL scripts**.
- **Up & Down Migrations:** Apply and rollback migrations **easily** using the **CLI**.
- **Dry-Run Mode:** Preview what migrations **will run** without applying any changes.
- **Migration Status:** View which migrations are **applied or pending**.
- **Supports .env Files:** Easily manage database paths using **environment variables**.

---

## 🚀 **Installation:**

QuackUp is available on **PyPI** and can be installed using **pip**:

```sh
pip install quackup
```

---

## 📂 **Project Structure:**

```plaintext
.
├─ migrations/
│    ├─ 2025_02_25_1450-00123abc_create_users_table/
│    │    ├─ up.sql
│    │    └─ down.sql
│    └─ 2025_02_25_1500-00456def_add_email_to_users/
│         ├─ up.sql
│         └─ down.sql
|- quackup.ini
└─ env.ini (optional)
```

---

## ⚡️ **Usage:**

### 1. 🆕 **Initialize QuackUp:**

```sh
quackup init
```

This will **automatically create** a **`quackup.ini`** configuration file and a **`migrations` directory** if they do **not already exist**:

```plaintext
.
├─ quackup.ini       # Configuration file for QuackUp
└─ migrations/       # Directory for storing migration files
```

The **`quackup.ini`** file will contain:

```ini
[quackup]
db_env_var = DUCKDB_PATH
```

You can then **set the database path** using a **`.env` file** or **environment variable**:

```plaintext
# .env file
DUCKDB_PATH=/path/to/your_database.duckdb
```

### 2. 🆕 **Create a New Migration:**

```sh
quackup create "Add email to users table"
```

This will generate a **timestamped migration folder** with **`up.sql`** and **`down.sql`** files:

```plaintext
migrations/
└─ 2025_02_25_1500-00456def_add_email_to_users/
     ├─ up.sql
     └─ down.sql
```

---

### 3. 🚦 **Apply All Pending Migrations:**

```sh
quackup up
```

Or **dry-run** to see which migrations **would be applied**:

```sh
quackup up --dry-run
```

---

### 4. 🔄 **Rollback Migrations:**

```sh
quackup down
```

Or **preview the rollback** actions:

```sh
quackup down --dry-run
```

---

### 5. 📋 **Check Migration Status:**

```sh
quackup status
```

Example Output:

```plaintext
Migration                                                   Status
----------------------------------------------------------------------
2025_02_25_1450-00123abc_create_users_table                  up
2025_02_25_1500-00456def_add_email_to_users                  down
```

---

## ⚠️ **Important Considerations:**

- Make sure your **duckdb file path** is configured correctly in quackup.
- **Always test migrations** in a **staging environment** before applying them in **production**.
- The **dry-run mode** is a great way to **verify what quackup will execute**.
- .env files can be used to **automatically set the environment variable** needed for quackup to connect to your duckdb database.

---

## 🤝 **Contributing:**

Contributions are welcome! If you find **bugs**, have **feature requests**, or want to **contribute**, please **open an issue** or **submit a pull request**.

---

## 📄 **License:**

This project is licensed under the **MIT License**. See the **LICENSE** file for details.
