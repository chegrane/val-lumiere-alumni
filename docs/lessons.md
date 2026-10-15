# Traps and lessons

**Goal of this file:** the mistakes we really made while building this project, and what they teach. Each one: what happened, a small example, the lesson, and where it lives in the project.

Most of them are classic: almost everyone who works with databases meets them once. The stories are real; the lesson at the end of each one is general, and works in any project.

---

## The method behind every lesson

Writing correct SQL is less about syntax than about **turning a real-world rule into behaviour the database enforces, and proving it**. Every rule goes through three steps, and the three must agree:

| Step | Example: *a person who withdraws consent must not receive another newsletter* |
|---|---|
| **1. The rule**, in plain words | A later refusal overrides an earlier approval |
| **2. The mechanism** that enforces it | The view `current_consent` picks the answer that counts today; `recipient` keeps only the "yes" |
| **3. The test**, valid **and** invalid cases | Karim says yes on January 15 and unsubscribes on March 2: his current answer is "no", and he is not on the newsletter list |

A correct rule with a wrong query is not enough; a correct query with no test is not enough either.

---

## Modelling

### 1. The same fact stored twice will one day contradict itself

**What happened.** First idea: one table for people and their degrees. Karim has two degrees, so he became two rows, with his name copied twice.

**The trap.** Change his name in one row and forget the other: the table now says two different things about the same person. This is an **update anomaly**.

**The lesson.** Store each fact **once** (normalisation): `Person` 1 ── 1..* `Degree`. The same trap came back later with imported lists: the date of a list was copied onto its 5,000 answers, until it got its own class, `SourceList`.

**In the project:** [model.md, 1.2](model.md#12-the-choices-one-by-one), decisions D-014 and D-028.

### 2. Counting people is not counting degrees

**What happened.** "How many graduates by faculty?" Karim has a degree in Science and one in Engineering.

**The trap.** He counts once in each faculty. Science 2 + Engineering 3 + Administration 1 + Education 1 = 7, but there are only **6** people.

**The lesson.** Say what you count. To count people in a group, `COUNT(DISTINCT person_id)`, not `COUNT(*)`. Never add the faculty totals of people.

**In the project:** [queries.md, Q1](queries.md#q1--how-many-graduates-do-we-have-by-faculty-and-by-year).

### 3. Keep the history; derive the current state

**What happened.** First idea for consent: one row per person, with a yes/no column per kind of message. Each new answer would overwrite the old one.

**The trap.** We could no longer say *since when* or *how* the person answered, nor prove it. And "the latest row" is not always the answer that counts: an old list imported today must not undo Robert's "stop".

**The lesson.** Store every decision as its own row (the evidence), and compute today's state in a view, with explicit rules. Never overwrite history to simplify today's query.

**In the project:** `consent` (the history) and `current_consent` (today), decisions D-016 and D-026.

---

## Constraints

### 4. `UNIQUE` is exact: "Science" and "science" are two faculties

**What happened.** With `name text UNIQUE`, PostgreSQL accepted both `Science` and `science`.

**The lesson.** Uniqueness compares values exactly. For a rule "whatever the case", index the **normalised** value:

```sql
CREATE UNIQUE INDEX faculty_name_lower_key ON faculty (lower(name));
```

**In the project:** every reference table, and contacts (`Lea@Example.org` = `lea@example.org`).

### 5. Spaces get past the uniqueness rule too

**What happened.** `' Engineering '` (with spaces) is not equal to `'Engineering'`, so it would enter as a second faculty, even with the index above.

**The lesson.** The database does not clean data; it **refuses dirty data**. A `CHECK` requires values already trimmed; cleaning is the import's job (slice 4):

```sql
CHECK (name <> '' AND name = btrim(name))
```

**In the project:** every `…_trimmed` constraint in [01_schema.sql](../sql/01_schema.sql).

### 6. `NOT NULL` means "not missing", not "not blank"

**The trap.** `NOT NULL` refuses `NULL`, but accepts `''` (an empty text) and `'   '`.

**The lesson.** Two different rules: `NOT NULL` (a value is given) and `name <> ''` (the value has content).

### 7. `NULL` is not a value: it means "unknown"

**The traps.**
- `NULL = NULL` is not true: it is unknown. Write `x IS NULL`, never `x = NULL`.
- `UNIQUE` accepts **several** `NULL`s: two unknowns are not "equal". That is exactly what we want for `student_number`: unique when present, missing in many old spreadsheets.
- `COUNT(*)` counts rows; `COUNT(student_number)` counts only the rows where it is not `NULL`.

**The lesson.** SQL does not use two-valued logic (true, false) but three (true, false, unknown). Every rule must say what happens when a value is missing.

### 8. The NULL trap: a `CHECK` accepts `NULL`

**What happened.** The rule "a request has a reason only if it was refused or partly done" was written:

```sql
CHECK (reason_code IS NULL OR outcome IN ('partly done', 'refused'))
```

An **open** request (outcome `NULL`) with a reason passed: `FALSE OR NULL` = `NULL`, and **a `CHECK` accepts a row when its test is true *or NULL***. A corrected version, listing three cases with `AND`/`OR`, fell into the same trap one level deeper.

**The lesson.** In a rule across columns, use only `IS NULL` / `IS NOT NULL`, which are never `NULL`:

```sql
CHECK ((reason_code IS NOT NULL) = (outcome IS NOT NULL AND outcome <> 'done'))
```

**And a second lesson:** two careful reviews (one by each AI assistant) missed it. Ten seconds of running it on PostgreSQL found it (lesson 21).

**In the project:** `request_reason_matches_outcome` in [01_schema.sql](../sql/01_schema.sql).

### 9. A `CHECK` sees only its own row

**The trap.** "After a removal, a degree's source is only 'registrar' or 'spreadsheet'" depends on `person.removed_on`, a column of **another** table. A `CHECK` on `degree` cannot see it.

**The lesson.** Each kind of rule has its tool:

| Rule | Tool |
|---|---|
| Inside one row | `CHECK` |
| "This value exists over there" | Foreign key |
| "These two rows belong together" (the contact is **this person's**) | Foreign key on **two** columns `(contact_id, person_id)` |
| "This value never changes" | Trigger (a `CHECK` cannot see the old value) |
| Anything else across tables | A trigger, the import process, or a test |

**In the project:** [model.md, part 3](model.md#3-check) says, for each rule, which tool enforces it.

### 10. A rule written in a comment is not a rule the database enforces

**What happened.** Twice, the schema *said* a rule that the database did not *enforce*:
- A consent pointed to a person **and** to a request, with two ordinary foreign keys. Each one checks that its row exists, but nothing checked that the request was **the same person's**. Léa's consent could point to Robert's request.
- A trigger checked that the contact chosen by a consent is an email, but only when the **consent** changes. Changing the **contact** from email to phone afterwards went around it.

**The lesson.** For each rule, ask: *what invalid state could the database still accept?* A constraint protects only what it actually checks; a trigger protects only the operation it is attached to. Here: a foreign key on two columns `(request_id, person_id)`, and a contact's kind made unchangeable.

**In the project:** `consent_request_fk` and `contact_kind_value_never_change` in [01_schema.sql](../sql/01_schema.sql).

### 11. Foreign keys are not indexed automatically

**The trap.** In PostgreSQL, a `PRIMARY KEY` or `UNIQUE` creates an index; a `REFERENCES` does **not**. Looking up "all the requests of this person" may scan the whole table.

**The lesson.** Index the foreign keys that real queries use (`request(person_id)`, `registration(event_id)`), and add the others only when a measurement shows the need.

---

## How PostgreSQL behaves

### 12. Identifiers have gaps: a surrogate key is a label, not a counter

**What happened.** After two failed inserts, the faculties were numbered 1, 2, **5**.

**Why.** A number is handed out **before** the constraints are checked, and never taken back, even on failure. Guaranteeing no gaps would make every insert wait for the previous one: PostgreSQL chooses speed.

**The lesson.** Never rely on identifiers being consecutive. "How many?" is `COUNT(*)`, never the largest id.

### 13. Without `ORDER BY`, the order of rows is not guaranteed

**What happened.** After an `UPDATE`, faculty 1 appeared **last** in `SELECT * FROM faculty`.

**Why.** PostgreSQL never overwrites a row: an `UPDATE` writes a **new version** of it and marks the old one dead (this is called MVCC, multi-version concurrency control).

**The lesson.** If the order matters, write `ORDER BY`. Always.

### 14. Turning a timestamp into a date depends on the time zone

**The trap.** `received_at::date` uses the time zone of the connection. A list received at 22:30 in Montréal is already the **next day** in UTC.

**The lesson.** Types must carry the meaning of the data, and conversions the business context. Say which calendar you mean: `(received_at AT TIME ZONE 'America/Montreal')::date`, the office's day.

---

## Queries and views

### 15. Joining people with their degrees duplicates people

**The trap.** To invite "Mathematics graduates of 1995–2000", a `JOIN` with `degree` gives **one row per degree**: a person with two matching degrees is invited twice.

**The lesson.** When a list targets people, ask "**does there exist** a degree such that…": `EXISTS (…)` answers yes or no once per person.

**In the project:** [queries.md, list B](queries.md#list-b--a-department-event-mathematics-graduates-of-1995-to-2000).

### 16. No row is not "no"

**The trap.** Gérard has no consent row. That does not mean he refused: he was **never asked**.

**The lesson.** An absent row, a `NULL` and a "no" are three different things. A report of "who refused" must list explicit "no" answers only.

### 17. Can and may are two different tests

**The lesson.** Start from the business questions, not from the SQL. *Can* we reach the person (a working email)? *May* we contact them (their consent)? Two questions, two views (`sendable_email`, `current_consent`), combined by a third (`recipient`). A mailing list needs **both**. And the two gaps are different problems: Sophie (may, but her email bounced) is a data quality task; Robert (we can, but he said stop) must be respected.

**In the project:** [queries.md](queries.md#can-we-reach-them-and-may-we-contact-them).

### 18. When rows compete, specify the complete precedence

**What happened.** In `current_consent`, several answers compete for the same person and kind of message. Each line of the `ORDER BY` decides one thing: the latest date first; on the same day, "no" first; same day and same answer, the person's own choice before a list; then two tie-breakers so the result never changes. The line "the person's own choice first" was missing at first: the decision was still right ("no"), but the report showed "a list blocks" instead of "Robert refused".

**The lesson.** When several rows compete, write the **whole** precedence rule, down to the last tie. Never assume the first row the database returns is the right one.

**In the project:** `current_consent` in [02_views.sql](../sql/02_views.sql).

### 19. A view is an interface: show only what is needed

**What happened.** The first version of `active_person` was `SELECT * FROM person`. Anyone reading the view would also see the student number and the birth date, although no list needs them.

**The lesson.** A view is not only a shortcut: it is a **window** on the data. List the columns it exposes, and only those its users need (`person_id`, `first_name`, `last_name`). In slice 5, the roles will read views, not tables: what the view does not show, they cannot see.

**In the project:** `active_person` in [02_views.sql](../sql/02_views.sql).

### 20. Plain view or materialized view?

| | Plain view | Materialized view |
|---|---|---|
| What it is | A **saved query**: nothing is stored | A **stored result**, like a table |
| When it is computed | Each time it is read | When you run `REFRESH MATERIALIZED VIEW` |
| Always up to date? | Yes | Only just after a refresh |
| Speed | Pays the computation on each read | Fast to read |

**The trap.** A materialized view refreshed every night is **stale** during the day. If consent were one, Robert's "stop" at 10:00 would only count after midnight, and the 14:00 invitations would still include him.

**The lesson.** Choose by what staleness costs. Consent must always be fresh: a **plain** view (`current_consent`). Statistics a few hours old harm no one, and they are heavy: a good candidate for a **materialized** view. And do not optimise before measuring: at our size (about 60,000 people), the plain view is fast.

**In the project:** [02_views.sql](../sql/02_views.sql), [queries.md, Q1](queries.md#q1--how-many-graduates-do-we-have-by-faculty-and-by-year).

---

## Working method

### 21. Tests beat reviews; test what must be refused

Three internal review rounds and several outside reviews improved the model a lot, but missed the NULL trap (lesson 8). Running the SQL found it at once. Reviews are good at structure and wording; **only execution proves that a rule holds**.

And testing only valid examples is not enough. For each rule, write one case that must **pass** and one that must be **refused**: missing values, conflicting rows, ties, unexpected updates, rows from different people. A schema that loads without errors proves only that the SQL can be created, not that it enforces the rules.

**In the project:** the edge cases of [queries.md](queries.md#edge-cases-to-test) and the schema's refusal checks in `tests/` become automatic tests.

---

## In short

- **Start from the business rule**, then translate it into tables, constraints, views and tests.
- **Know what each tool can see:** a `CHECK` its own row; a foreign key one link; a trigger only the operation it is attached to.
- **`NULL` is a third value.** A `CHECK` lets it through.
- **Keep the evidence; derive today's state** with explicit rules, down to the last tie.
- **Make ambiguity explicit:** which time zone, which order, absent versus "no".
- **Design views as interfaces:** one rule written once, and only the columns that are needed.
- **For every rule: state it, enforce it, and test what must pass and what must be refused.**
