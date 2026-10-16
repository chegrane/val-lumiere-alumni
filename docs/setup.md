# Setup — step by step

This tutorial is for beginners. Every command is explained word by word, with what you should see.
If you already know Linux and PostgreSQL, the short version in the [README](../README.md#setup) is enough.

**What you will have at the end:** PostgreSQL running, your own database user, the project database, and the project files.

**Tested on:** Windows 11 with Ubuntu 26.04 under WSL2, PostgreSQL 18.6 (October 2026).

| Your system | Start at |
|---|---|
| Windows | [Part 1](#part-1--windows-only-get-ubuntu-with-wsl2) |
| Ubuntu or Debian | [Part 2](#part-2--install-postgresql) |
| macOS or another Linux | Install PostgreSQL from [postgresql.org/download](https://www.postgresql.org/download/), then continue at [Step 4](#step-4--create-your-own-database-user) |

> **Rule:** type one command at a time. If what you see does not match "You should see", stop and read the error before going further.

---

## Part 1 — Windows only: get Ubuntu with WSL2

**Why:** the project runs on Linux, like most database servers. WSL2 (Windows Subsystem for Linux) runs a real Ubuntu inside Windows, without a virtual machine to manage.

Open **PowerShell as administrator** and type:

```bash
wsl --install
```

| Word | Meaning |
|---|---|
| `wsl` | The Windows tool that manages Linux systems |
| `--install` | Install WSL2 and Ubuntu (the default distribution) |

Restart Windows when asked, then open **Ubuntu** from the Start menu. The first time, it asks you to choose a Linux user name and password.

> In this project, WSL and Ubuntu were installed before the tutorial was written. This step is Microsoft's standard command; see the [official guide](https://learn.microsoft.com/windows/wsl/install) if anything differs.

**From now on, every command is typed in the Ubuntu terminal**, not in PowerShell (unless said otherwise).

---

## Part 2 — Install PostgreSQL

### Step 1 — Update the list of packages

**Why:** Ubuntu installs software from online lists ("packages"). We refresh the list, then upgrade what is already installed.

```bash
sudo apt update
```

```bash
sudo apt upgrade -y
```

| Word | Meaning |
|---|---|
| `sudo` | Run the command as administrator (`root`). It asks for your Ubuntu password; nothing appears while you type, which is normal |
| `apt` | Ubuntu's package installer |
| `update` | Refresh the list of available packages (installs nothing) |
| `upgrade` | Install the newer versions of what you already have |
| `-y` | Answer "yes" to the confirmation question |

**You should see:** a list of downloads, then the prompt again. Warnings are common; errors (`E:`) are not.

> **WSL tip:** after a large upgrade, restart WSL so that every service starts cleanly. In **PowerShell** (Windows side): `wsl --shutdown`, then reopen Ubuntu.

### Step 2 — Install PostgreSQL

```bash
sudo apt install -y postgresql
```

| Word | Meaning |
|---|---|
| `install` | Install a package |
| `postgresql` | The PostgreSQL server **and** the `psql` client |

The installation also creates a Linux user named `postgres`: the administrator of the database server.

### Step 3 — Check that it runs

```bash
psql --version
```

**You should see:** `psql (PostgreSQL) 18.x` (or another recent version).

```bash
sudo systemctl status postgresql
```

| Word | Meaning |
|---|---|
| `systemctl` | The tool that manages services (programs running in the background) |
| `status postgresql` | Show whether the PostgreSQL service is running |

**You should see:** `active (exited)` or `active (running)`. Press `q` to leave the screen.

---

## Part 3 — Your database user and the project database

### Step 4 — Create your own database user

**Why:** PostgreSQL starts with one administrator, `postgres`. Working every day as administrator is risky. We create a **role** (a database user) with your own name and only the right to create databases.

```bash
sudo -u postgres createuser --createdb $USER
```

| Word | Meaning |
|---|---|
| `sudo` | Run a command with another user's identity (by default `root`) |
| `-u postgres` | …here as the Linux user `postgres`, the only one PostgreSQL trusts as administrator at the start |
| `createuser` | A PostgreSQL program that creates a role |
| `--createdb` | A **permission**: this role may create databases. It does not create a database |
| `$USER` | Your Linux user name, filled in automatically |

**You should see:** nothing. No message means success.

**Why no password?** On the same machine, PostgreSQL uses **peer authentication**: it asks Linux "which user is this?" and lets you in as the role with the **same name**. No password is stored anywhere, which is why the role must be named like your Linux user.

The SQL equivalent, for reference: `CREATE ROLE your_name LOGIN CREATEDB;`

### Step 5 — Test everything with a temporary database, then delete it

**Why:** before building anything, check the whole chain — your role can create a database, you can connect without a password, PostgreSQL stores data and enforces rules. **Everything in this step is temporary.**

**5a. Create a test database**

```bash
createdb val_lumiere_test
```

| Word | Meaning |
|---|---|
| `createdb` | A PostgreSQL program that creates a database. No `sudo`: your role has the right since Step 4 |
| `val_lumiere_test` | Its name; `_test` means "temporary" |

**You should see:** nothing.

**5b. Connect to it**

```bash
psql val_lumiere_test
```

| Word | Meaning |
|---|---|
| `psql` | The PostgreSQL terminal, where you type SQL |
| `val_lumiere_test` | The database to open. The user is your Linux name |

**You should see:** the prompt `val_lumiere_test=>`. You are now inside PostgreSQL. Every SQL statement ends with `;`.

**5c. Try a small table** (one line at a time)

```sql
SELECT version();
```

Shows the server version: the server answers.

```sql
CREATE TABLE test_person (id integer PRIMARY KEY, name text NOT NULL);
```

| Word | Meaning |
|---|---|
| `CREATE TABLE test_person` | Create a table named `test_person` |
| `id integer PRIMARY KEY` | Column `id`, whole numbers; **primary key** = unique and never empty |
| `name text NOT NULL` | Column `name`, text; **NOT NULL** = required |

```sql
INSERT INTO test_person VALUES (1, 'Marie Tremblay');
```

Adds one row (a fictional name). **You should see:** `INSERT 0 1`.

```sql
SELECT * FROM test_person;
```

Reads the table (`*` = all columns). **You should see:** your row.

```sql
INSERT INTO test_person VALUES (1, 'Another Person');
```

**This one must fail:** `ERROR: duplicate key value violates unique constraint`. Every relational database rejects a second `id = 1`.

```sql
SELECT '2026-02-30'::date;
```

**This one must fail too:** `ERROR: date/time field value out of range`. February 30 does not exist. Here PostgreSQL differs from more permissive systems: it is strict by default, and no setting makes it accept invalid values. That is why this project uses it.

**5d. Look around, then leave**

| Command | Meaning |
|---|---|
| `\du` | List the roles: you should see yours (`Create DB`) and `postgres` (`Superuser`…) |
| `\l` | List the databases and their owner. Press `q` if the list ends with `(END)` |
| `\q` | Quit `psql`, back to Linux |

Commands that start with `\` belong to `psql`, not to SQL: no `;` needed.

**5e. Delete the test database**

```bash
dropdb val_lumiere_test
```

| Word | Meaning |
|---|---|
| `dropdb` | Delete a database **and everything inside it** |
| `val_lumiere_test` | Only the test database |

**You should see:** nothing. The chain works.

### Step 6 — Create the project database

```bash
createdb val_lumiere_alumni
```

It stays empty until the schema is loaded (coming in a later stage of the project).

---

## Part 4 — Get the project

### Step 7 — Tell Git who you are

**Why:** every commit records an author. You do this once per machine (Git in Ubuntu is separate from Git on Windows).

```bash
git config --global user.name "Your Name"
```

```bash
git config --global user.email "you@example.com"
```

| Word | Meaning |
|---|---|
| `git config` | Read or change a Git setting |
| `--global` | For all your repositories (saved in `~/.gitconfig`) |
| `user.name` / `user.email` | The setting |

> The email is visible in the history of public repositories. GitHub offers a private address: Settings → Emails → "Keep my email addresses private".

Check with `git config --global --list`.

### Step 8 — Clone the repository into the Linux file system

```bash
mkdir -p ~/projects
```

```bash
git clone https://github.com/chegrane/val-lumiere-alumni.git ~/projects/val-lumiere-alumni
```

| Word | Meaning |
|---|---|
| `mkdir -p` | Make a directory; no error if it exists |
| `~` | Your home folder (`/home/<you>`) |
| `git clone` | Copy a repository with its whole history |

> **Windows users:** keep the project in `~/projects` (Linux side), **not** in `/mnt/c/...` (your Windows drive). It is faster, and file permissions behave like on a real Linux server.

```bash
cd ~/projects/val-lumiere-alumni
```

`cd` = change directory. Then `git log --oneline` shows the history.

---

## Part 5 — Optional: push to GitHub with an SSH key

Only needed to **send** commits to your own GitHub repository.

**Why SSH:** your computer keeps a **private** key; GitHub gets the matching **public** key. On each push, GitHub checks that they match. No password travels.

### Step 9 — Create the key

```bash
ssh-keygen -t ed25519 -C "my-laptop"
```

| Word | Meaning |
|---|---|
| `ssh-keygen` | Create an SSH key pair |
| `-t ed25519` | Key type: the modern standard |
| `-C "my-laptop"` | A label to recognise the key; not a password |

Press **Enter** for the file location. For the **passphrase**, two choices:

| Choice | You type | Trade-off |
|---|---|---|
| Empty (press Enter twice) | Nothing, ever | Your session password protects the key. If the laptop is lost, delete the key on GitHub |
| A passphrase | It, on each push (or once per restart with a tool such as `keychain`) | The key is protected even if the file is stolen |

Two files now exist: `~/.ssh/id_ed25519` (**private**: never share it) and `~/.ssh/id_ed25519.pub` (public).

### Step 10 — Give the public key to GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

`cat` prints the file. Copy the whole line (`ssh-ed25519 AAAA…`), then on GitHub: Settings → SSH and GPG keys → New SSH key → paste → Add.

### Step 11 — Test

```bash
ssh -T git@github.com
```

| Word | Meaning |
|---|---|
| `-T` | No interactive terminal: we only test identity |
| `git@github.com` | GitHub's server; it recognises **you** by your key |

The first time, compare the fingerprint shown with GitHub's page "GitHub's SSH key fingerprints", then type `yes`.
**You should see:** `Hi <your-username>! You've successfully authenticated…`

### Step 12 — Link and push

```bash
git remote add origin git@github.com:<your-username>/<your-repo>.git
```

```bash
git push -u origin main
```

| Word | Meaning |
|---|---|
| `git remote add origin` | Add a link named `origin` to the online copy |
| `git push` | Send your commits |
| `-u` | Remember the link: next time, `git push` alone is enough |

---

## Part 6 — Optional: VS Code on Windows

1. In VS Code, install the **WSL** extension (published by Microsoft).
2. `F1` → **WSL: Connect to WSL** → File → Open Folder → `/home/<you>/projects/val-lumiere-alumni`.
3. The bottom-left corner shows **WSL: Ubuntu**; the terminal (`` Ctrl+` ``) runs in Ubuntu.

If VS Code misbehaves the first time, close it and open it again.

---

## Part 7 — Build the database and prepare Python

### Step 13 — Build the database in one command

From the project folder:

```bash
scripts/reset_db.sh
```

It deletes the database `val_lumiere_alumni`, recreates it, and runs the three SQL files in order: the schema, the views, the test data ([sql/README.md](../sql/README.md)). **You should see:** three `== sql/0…` lines, then `Database val_lumiere_alumni rebuilt.`

> If you see `Permission denied`, the script lost its execute permission: `chmod +x scripts/reset_db.sh`.

### Step 14 — A virtual environment for Python

**Why:** each project gets its **own private folder of libraries** (`.venv`), separate from the system's Python. Its versions disturb nothing else, and anyone can rebuild the same environment from `requirements.txt`.

```bash
sudo apt install -y python3-venv
```

```bash
python3 -m venv .venv
```

| Word | Meaning |
|---|---|
| `python3 -m venv` | Run Python's `venv` **m**odule |
| `.venv` | The folder to create. Hidden (the `.`), and excluded from Git by `.gitignore` |

```bash
source .venv/bin/activate
```

| Word | Meaning |
|---|---|
| `source` | Run a file **inside the current shell** (a shell built-in, because it must change this shell) |
| `.venv/bin/activate` | Switches `python` and `pip` to the project's own |

**You should see:** `(.venv)` at the start of the prompt. Each new terminal starts without it: run `source` again. `deactivate` leaves it.

### Step 15 — Install the libraries

```bash
pip install -r requirements.txt
```

`pip` installs every library listed in [requirements.txt](../requirements.txt):

| Library | Role |
|---|---|
| `pytest` | Runs the automatic tests |
| `psycopg[binary]` | The **driver** that connects Python to PostgreSQL |

**Check:**

```bash
python -c "import psycopg, pytest; print(psycopg.__version__, pytest.__version__)"
```

**You should see:** two version numbers (tested with psycopg 3.3.6 and pytest 9.1.1).

### What is a database driver?

Every language uses a **driver** to talk to a database: JDBC in Java, ADO.NET in C#, **psycopg** in Python. It opens a connection, sends the SQL text, receives the rows, and converts the types (a PostgreSQL `date` becomes a Python `date`, `NULL` becomes `None`).

psycopg relies on **libpq**, PostgreSQL's official C library (the one `psql` uses). `psycopg[binary]` ships it **already compiled**, so nothing else needs to be installed.

A first connection, to try in `python`:

```python
import psycopg
conn = psycopg.connect("dbname=val_lumiere_alumni")    # no password: peer authentication
cur = conn.cursor()
cur.execute("SELECT first_name, last_name FROM person WHERE student_number = %s", ("VL1998042",))
print(cur.fetchone())                                   # ('Karim', 'Haddad')
conn.close()
```

**The value travels separately from the SQL text** (`%s`, then the value). This is a **parameterized query**, the protection against SQL injection: a value is never pasted into the SQL string.

### Step 16 — Run the tests

With `(.venv)` active, from the project folder:

```bash
pytest
```

`pytest` finds the tests in `tests/`, rebuilds a **separate** test database (`val_lumiere_test`, so `val_lumiere_alumni` is never touched), and runs each test inside a transaction that is cancelled afterwards.

**You should see:** a dot per passing test, then a summary such as `77 passed, 2 skipped`. The two skipped tests wait for the imports of slice 3.

| Option | Meaning |
|---|---|
| `pytest -v` | **V**erbose: one line per test, with its name |
| `pytest -k removal` | Run only the tests whose name contains "removal" |
| `pytest -x` | Stop at the first failure |
