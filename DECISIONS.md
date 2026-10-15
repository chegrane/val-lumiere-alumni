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

### D-027 — Two AI assistants, with clear roles (2026-10-12)
- **Choice:** Claude for discussion, structure, model, SQL, code and first drafts; ChatGPT for outside review and for the texts (flow, consistency, clarity, English and French). Ibrahim decides and accepts everything. One ChatGPT pass per milestone; Claude applies reviews with judgment and says when it disagrees.
- **Why:** the outside reviews found real errors that three internal rounds had missed (a model of the same family shares the same blind spots), and ChatGPT writes very clear prose. Saying who helped is also a matter of honesty: the README now names both.
- **Rejected:** one assistant only (no outside viewpoint); a ChatGPT review on every change (loops where the two rewrite each other, and the free plan's limits).

## Model (slice 1)

### D-014 — A person and their degrees are two classes (2026-10-10)
- **First idea:** one table holding the person and their degree (name, birth date, faculty, program, year…). Simple, and every statistic is one filter away.
- **Problem:** a person with two degrees becomes two rows, with name and birth date copied twice. Change the name in one row and not the other, and the table itself has created the duplicate the story complains about.
- **Choice:** `Person` 1 ── 1..* `Degree` (normalisation: each fact stored once). Every person has at least one degree.

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

### D-019 — Removal and the do-not-contact list (2026-10-10)
*Wording corrected by D-022; the rule for new degrees replaced by D-023.*
- **First idea:** on removal, empty the names but keep the student number on the `Person` row when the person had said "stop".
- **Problem:** the kept degrees point to that row: student number + program + year identifies the person again. And a removal erased the death record, so a deceased graduate could come back from an import and be invited.
- **Choice:** removal empties every identifying attribute (names, student number, birth date, death information, name at graduation) and detaches the kept requests from the person. For **every** removal, the student number alone goes into `DoNotContact` (a *suppression list*), with the reason (`deceased`, `stop` or `removed`) and the date; it is linked to nothing. The list means "never contact, for anything": any stop becomes total at removal. A listed number only ever creates anonymous data: imports ignore its old degrees; a new degree is attached to a new, already-removed person (people counted twice in that rare case; degree totals stay right).
- **Why every removal:** with the student number emptied, the next import would bring the person back with full identity, and count their degrees twice.
- **Accepted limits:** a person without a student number cannot be recognised after removal; dates can still hint at a link; archived spreadsheets follow the university's retention rules.

### D-020 — The current consent answer, and imports (2026-10-10)
*Replaced by D-024.*
- **Problem:** with a date only, a "yes" and a "stop" given the same day are tied; and an old list imported today could hide an earlier "stop".
- **Choice:** two moments per answer: `given_on` (when the person answered) and `recorded_at` (when we recorded it). One rule, independent of the order of imports: an answer given directly by the person (email, phone, letter) always wins over an imported one; among direct answers, the latest `given_on` wins, then the latest `recorded_at`; with only imported answers, any "no" wins.
- **Also:** a consent may name an email of the same person; if it stops working, nothing is sent for that kind of message (no fallback to another address).
- **Rejected:** ordering by the date of entry only (an import would always win); ordering imported answers by their dates (an undated "no" could lose, depending on the import order).

### D-021 — Left for later, on purpose (2026-10-10)
- **Deferred to slices 3–4:** staging tables for raw imports; where duplicate decisions are kept and how two people are merged; dated quality measurements for "better or worse, month after month".
- **Accepted limit:** a program belongs to one faculty, without history.
- **Why:** part 1 of the model stores what the story needs every day; these belong to the import and quality work, and will be designed with it.

### D-022 — Removal is de-identification plus a suppression list, not anonymisation (2026-10-12)
- **Problem (outside review, ChatGPT):** the model said "everything that identifies the person goes", but the student number is kept on the suppression list, and a kept degree (program + year) can point to one person in a small program.
- **Choice:** keep the degree rows on an emptied `Person`, and the student number alone on the suppression list. Describe it honestly: **removal = de-identification + suppression list**, not anonymisation. State the residual risk for small programs.
- **Rejected:** deleting the degree rows and keeping only anonymous totals (stronger privacy, but every statistic must add those totals: more complex for this project).

### D-023 — A new degree for a listed number is ignored (2026-10-12)
- **Fact:** old spreadsheets are imported once; afterwards the registrar sends only new degrees. So a degree arriving for a listed number is new.
- **Choice:** ignore it. A listed number never enters again, for anything. The degree totals miss this rare case; the limit is written down.
- **Rejected:** attaching it to a new, already-removed person (exact degree totals, but more logic, and the person counted twice).

### D-024 — Consent: the effective date decides; on the same date, "no" wins (2026-10-12)
*Its ordering rule is replaced by D-026; the split of `channel` and `entry` stays.*
- **Problem (outside review, ChatGPT):** the column `channel` mixed *how the person answered* with *how the record entered the database*. An unsubscribe link arrives through Office 365, counted as "import", and lost to an older direct "yes".
- **Choice:** two separate attributes: how the person answered (email, phone, letter, unsubscribe link…) and how the record entered (typed by staff, imported file, mailing system). Each answer has an **effective date**: the date the person answered, or, for an old list without dates, the date of that list. **The latest effective date wins; on the same date, "no" wins.**
- **Why:** the result does not depend on the order of imports; an unsubscribe beats an older "yes"; a new "yes" after a "no" is respected.
- **Rejected:** "direct answers always beat imported ones" (D-020: fails on unsubscribe links); "any 'no' always wins over imports" (an old wrong "no" would block the person until they contact the office).

### D-025 — Faculty at graduation stored on each degree (2026-10-12)
- **Problem (outside review, ChatGPT):** with only `Program` → `Faculty`, past degrees follow a program that moves to another faculty, and historical statistics change.
- **Choice:** `Degree` gets the faculty at graduation, as given by the registrar. `Program` keeps its current faculty.
- **Why it is not duplication:** it is a historical fact, true on the day of graduation, and it may differ from the program's faculty today.
- **Rejected:** keeping only `Program` → `Faculty` and noting the limit.

### D-026 — Consent: three kinds of evidence (2026-10-12)
- **Problem (outside review, ChatGPT):** under D-024, a list's date counted as the person's choice. A stale list exported on March 10 still saying "yes" would beat a "stop" given on March 2. And a bare "yes" in an old list does not prove a valid, specific consent.
- **Choice:**
  1. **The person's own choice**, with its real date (typed by the staff, unsubscribe link): the latest wins; on the same date, "no" wins.
  2. **A "no" from a list** blocks contact from the day we receive the list. An import can never reopen contact; only a later choice by the person can.
  3. **A "yes" from a list** counts only when there is nothing else, **and** only if the list documents a real, specific consent (for example, the newsletter sign-up form). Otherwise the permission is **unknown**: nothing is sent, and the person is asked to confirm.
  - *Added 2026-10-14:* on the same day with the same answer, the person's own choice is shown rather than a list's (the decision is unchanged; only the provenance shown, so that Q6 says who refused).
  4. Three dates are kept apart: the day of the choice (`Consent.given_on`), the date a list represents and the day we received it (both on `SourceList`, D-028). A file's export date is never taken as the day of a choice.
- **Why:** correct (an unproven "yes" is not consent), prudent (a list can block, never reopen), and no campaign to ask everyone again: documented lists keep working.
- **Rejected:** D-024 (a list's date counted as a choice); ignoring every imported "yes" (the office would start with nobody to write to).

### D-028 — SourceList: the description of an imported list belongs to the list (2026-10-14)
- **Problem (outside review, ChatGPT):** where is the proof behind a "documented" list, and what if proof is found later? Underneath: the list's date and its "documented" flag were copied onto every answer from that list. 5,000 answers, 5,000 copies: an update anomaly.
- **Choice:** a class `SourceList`, one row per imported list and per kind of contact: when it was received, the date it represents, whether it proves consent, where the proof is, when and by whom it was checked. Each imported answer points to its list. A list snapshot never carries a choice date (`given_on` empty).
- **Why:** each fact stored once (normalisation); proof found later is recorded on one row, with its date and checker, without changing any answer; evidence is specific to one kind of contact (a newsletter form does not prove consent to assignment offers).
- **Rejected:** a proof reference on each consent row (the same duplication); a full history of every change of evidence status (not needed for this version).

## Open questions

- **Sort order of French names:** the database uses the default `C.UTF-8` collation, which sorts `Émilie` after `Zoé`. Decide in slice 2 whether to use a French (Canada) collation.
- **Licence:** MIT proposed, to confirm before going public.
