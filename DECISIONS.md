# Decisions

Every choice made in this project: **the choice**, **why**, and **the option rejected**.
Decisions are taken by Ibrahim Chegrane; proposals and comparisons were prepared with an AI assistant (Claude).
Newest entries at the bottom.

## Project framing

### D-001 — Synthetic data only (2026-10-07)
- **Choice:** every name, address and record is invented (generated with Faker).
- **Why:** the project is public and about personal information; real data would contradict its purpose.
- **Rejected:** real or "anonymised" real data.

### D-002 — Name: `val-lumiere-alumni` (2026-10-08)
- **Choice:** keep the fictional name Université de Val-Lumière; state "fictional institution" on the first line of the README and in the repository description.
- **Why:** a realistic name makes the project feel real; the warning removes any confusion. "Alumni" fits any school (university, CEGEP, college).
- **Rejected:** a name with "db" (the project will go beyond the database); an obviously fictional name (Luna, Galaxy…).

### D-003 — Languages (2026-10-08)
- **Choice:** English for code and documents; `README.fr.md` with a full French summary; a French–English glossary; fake data in Canadian French (Québec names, addresses, postal codes).
- **Why:** English is the norm for code and readable by everyone; the French summary and glossary serve Québec readers; the story takes place in Québec.
- **Rejected:** two complete versions of every document (double maintenance; one version ends up abandoned). Full translations only at milestones.

### D-004 — Scope and order (2026-10-08)
- **Choice:** database and data quality first: 0 framing → 1 model → 2 SQL schema → 3 dirty synthetic data → 4 cleaning and duplicates → 5 consent, retention, deletion. Back end, front end and community features later.
- **Rule:** the next module may be explored privately, but is not officially started or published until the previous one is stable.
- **Why:** the core value is the model, data quality and respect for personal information; an interface would take months.
- **Rejected:** starting with a web application or an internal social network.

## Technical choices

### D-005 — PostgreSQL (2026-10-07)
- **Choice:** PostgreSQL as the database system.
- **Why:** free and open source (anyone can run the project); strict by default (rejects invalid types and values); full support for constraints, views, roles and access rights.
- **Rejected:** SQLite (lenient typing, no access rights); MySQL (valid, but no advantage for this purpose); Oracle and SQL Server (licences, hard for a visitor to reproduce).

### D-006 — Python: Faker, pandas, psycopg 3 (2026-10-07)
- **Choice:** Python, with Faker (synthetic data), pandas (cleaning), `psycopg` version 3 (PostgreSQL driver).
- **Why:** the most common language for data work; used daily by the author.
- **Rejected:** `psycopg2` (previous generation; version 3 is the current one for new projects).

### D-007 — SQL schema written by hand (2026-10-07)
- **Choice:** `sql/schema.sql` written by hand: tables, keys, constraints, indexes, views.
- **Why:** the project is meant to show the modelling; every line must be explainable.
- **Rejected:** an ORM (Django, SQLAlchemy) at this stage: it hides the SQL. It may come with the back end.

### D-008 — Diagrams in Mermaid (2026-10-07)
- **Choice:** diagrams written in Mermaid inside Markdown files.
- **Why:** GitHub displays them; they are versioned with the code and corrected in one line.
- **Rejected:** images (hard to keep up to date).

## Environment

### D-009 — Ubuntu under WSL2, project in the Linux file system (2026-10-08)
- **Choice:** develop in Ubuntu 26.04 under WSL2; the repository lives in `~/projects/val-lumiere-alumni`; VS Code connects through the WSL extension.
- **Why:** one environment for PostgreSQL, Python and Git, close to a real Linux server; faster file access and correct permissions.
- **Rejected:** the repository on the Windows drive with commands sent to Ubuntu (two environments, slower, permission problems); Docker (an extra layer not needed yet).

### D-010 — PostgreSQL from Ubuntu packages (2026-10-08)
- **Choice:** `sudo apt install postgresql` (version 18.6 installed).
- **Why:** one command, updated with the rest of the system.
- **Rejected:** the Windows installer (would split the environment).

### D-011 — Personal role with peer authentication, no superuser (2026-10-08)
- **Choice:** daily work with a role named like the Linux user, with only the `CREATEDB` right; local login by peer authentication (no password).
- **Why:** least privilege; no password to store, so none can leak into the repository.
- **Rejected:** working as the `postgres` superuser (too much power for daily work); password authentication for local development.
- **Later (slice 5):** separate roles with limited rights (for example an application role and a read-only analyst role).

### D-012 — Private GitHub repository until slices 0–2 are clean (2026-10-08)
- **Choice:** the repository is private for now and becomes public once the story, model and schema are clean.
- **Why:** publish a readable project, not a construction site.
- **Rejected:** public from the first commit.

## Working method

### D-013 — Two tracking files: `TASKS_TODO.md` and `ROADMAP.md` (2026-10-08)
- **Choice:** `TASKS_TODO.md` holds everything actionable (one current objective, an Inbox for bugs and ideas found along the way, next steps, done milestones); `ROADMAP.md` holds the phases of the project.
- **Why:** stay on one objective without losing what comes up; one place for the plan, so it cannot contradict itself.
- **Rejected:** a single `PROJECT_PLAN.md` or `ROADMAP.md` (mixes the big picture with daily tasks); GitHub Issues for now (simpler to start with a file; may come when the repository is public).

### D-018 — Fast, with understanding (2026-10-10)
- **Choice:** the AI assistant may draft documents, model and code; nothing is committed until Ibrahim understands and accepts it. Important parts are checked with a short quiz.
- **Why:** this is a personal learning project; speed matters, understanding matters more.
- **Rejected:** Ibrahim writing every file himself (slow, and the thinking is already shared in discussion); accepting drafts without checking (fast, but he could not explain them).

## Model (slice 1)

### D-014 — A person and their degrees are two classes (2026-10-10)
- **First idea:** one table holding the person and their degree (name, birth date, faculty, program, year…). Simple, and every statistic is one filter away.
- **Problem:** a person with two degrees becomes two rows, with name and birth date copied twice. Change the name in one row and not the other, and the table itself has created the duplicate the story complains about.
- **Choice:** `Person` 1 ── 0..* `Degree` (normalisation: each fact stored once).

### D-015 — Internal primary key; the student number is an attribute (2026-10-10)
- **First idea:** use the student number as the primary key, or build a code from the name (two letters of the family name, two of the first name, plus digits). It is unique and follows the person for life.
- **Problems:**
  1. Old spreadsheets (1990s) have no student number. A primary key cannot be empty, so these people could not be entered at all. This reason alone is decisive.
  2. Old files contain typing errors. Correcting a primary key means correcting it in every table that refers to it.
  3. The student number belongs to another system (the registrar). If its format changes or two records are merged there, our keys break. Common rule: do not use someone else's identifier as your own primary key.
  4. The student number identifies a person. As a key, it would be copied into every table that refers to people.
  5. A code built from the name changes when the name changes (Sophie Gagnon → Sophie Roy), and a key must never change.
- **Choice:** `person_id`, an internal number with no meaning outside our system, is the primary key. `student_number` is an attribute, `UNIQUE` and optional: the best way to **find** a person, not the key.

### D-016 — Consent: one row per person, per kind of contact, per answer (2026-10-10)
- **First idea (option A):** one row per person with one yes/no column per kind of contact (newsletter, events, offers).
- **Problems:** the previous answer is overwritten, so we cannot say since when or how the person answered (story question 6), and we cannot prove that consent was given. Adding a new kind of contact means changing the table.
- **Choice (option B):** one row per person, per kind of contact and per answer, with the date, the channel and who recorded it. The current answer is obtained with a view. The rows look repetitive, but each one is a different fact: the history.

### D-017 — Fields of expertise: many per person, from a shared list (2026-10-10)
- **Choice:** `Person` *──* `Field` through `PersonExpertise`. `Field` is a reference list, shared with the programs.
- **Why:** after years of work, a person knows several fields; assignment offers are sent "in the right field", which becomes a join instead of a comparison of free text.
- **Rejected:** one free-text "expertise" attribute on `Person` (one value only, and "civil engineering" typed five different ways).

## Open questions

- **Sort order of French names:** the database uses the default `C.UTF-8` collation, which sorts `Émilie` after `Zoé`. Decide in slice 2 whether to use a French (Canada) collation.
- **Licence:** MIT proposed, to confirm before going public.
