# CLAUDE.md — read this first, every session

Project: **val-lumiere-alumni**. Created on October 8, 2026 by Ibrahim Chegrane, with Claude.
Claude has no memory between sessions: everything that must last is in this repository.

## 1. Read before answering

1. `private/contexte_personnel.md` — personal context. Private, in French, never published.
2. `private/projet_diplomes_brief.md` — the story, the slices, the first entities, the five modelling questions, the long-term vision, the decisions on name and language (French).
3. `private/choix_techniques.md` — the technical choices **with their reasons** and the rejected options, including the comparison of database systems (French).
4. `TASKS_TODO.md` — **the current objective** and everything waiting (bugs, ideas, next steps). `ROADMAP.md` — the big picture.
5. `DECISIONS.md` and `docs/`.

If `private/` is missing (for example on another machine), ask Ibrahim for it before going further.

## 2. The goal in one paragraph

An **educational, open-source** project: the alumni database of a **fictional** institution, Université de Val-Lumière (it could equally be a CEGEP or any school). The short-term goal is a clean, public, runnable repository that demonstrates **data modelling, data quality and respect for personal information** — a personal learning project in database design and data quality. Long term, the project may grow into back end, front end and community features; those come later.

## 3. Decisions already taken (do not reopen without Ibrahim)

| Topic | Decision |
|---|---|
| Name | `val-lumiere-alumni`; "fictional institution" stated on the first line of the README and in the repo description |
| Scope now | **Database + fake data generation + data quality.** No web interface yet |
| Order | 0 framing → 1 model → 2 SQL schema → 3 dirty synthetic data → 4 cleaning, duplicates, quality report → 5 consent, retention, deletion. Then back end → front end → messaging/broadcast/chat → events and paid assignments |
| Module rule | The next module may be explored privately, but is not officially started or published until the previous one is stable |
| DBMS | **PostgreSQL** (strict, free, constraints, views, roles). SQLite and MySQL rejected for this purpose; Oracle and SQL Server excluded (licences) |
| Environment | Ubuntu under **WSL2**, `sudo apt install postgresql`, VS Code with the WSL extension. No Docker for now |
| Language (code) | **Python**: Faker (synthetic data), pandas (cleaning), `psycopg` version 3 (not psycopg2) |
| Schema | **SQL written by hand** (`sql/schema.sql`). No ORM until the back-end stage |
| Diagrams | **Mermaid** in Markdown files |
| Languages | **English** for code and documents; **`README.fr.md`** with a full French summary; a French–English **glossary** (`docs/glossary.md`); fake data in **Canadian French** (Québec names, addresses, postal codes). Full translations only at milestones |
| Data | **Synthetic only.** Never a real name or real data |
| Licence | MIT for the code, CC BY 4.0 for the documentation (D-030) |

## 4. How to work with Ibrahim

- **He decides the model.** Claude proposes, explains, criticizes; it never decides for him. Everything in the repo must be something he can explain without notes.
- **Fast, with understanding.** This is a personal project, not an assignment. Claude may draft anything (documents, model, code) to move fast; **nothing is committed until Ibrahim understands and accepts it**. For important parts, Claude checks with a short quiz (5–6 questions, file closed) and reworks what he cannot explain.
- **Make him understand.** He is a developer with a Ph.D. in computer science (approximate string matching) and solid university training in modelling and SQL; he is **not** a database administrator.
- **His expertise matters here:** duplicate detection between people records is approximate string matching (edit distance), the subject of his thesis. Give it a central place in slice 4.
- **Short answers:** 3 to 5 bullets, one idea per bullet, unless he asks for detail.
- **Truth:** never describe as done what is not done. The README says plainly that this is a personal project built with help from an AI assistant for part of the code.
- **Check the time** with `TZ=America/Montreal date` before dating anything.
- **One commit per working session**, even small. Every choice goes into `DECISIONS.md`: the choice, the reason, the rejected option.
- **Work sessions are 1 h 30** (project block: 13:00–14:30). Remind him **once** at the end of the block; then follow his choice. He often chooses to keep working.
- **Two assistants, clear roles.**

  | Who | Role |
  |---|---|
  | Ibrahim | Decides everything; nothing is committed until he understands and accepts it |
  | Claude | Discussion, structure, model, SQL, code, first drafts; applies reviews after checking them |
  | ChatGPT | Outside review (a different viewpoint), and above all the texts: flow, consistency, clarity, English and French |

  Order of steps: Claude drafts → Ibrahim reads → ChatGPT reviews (one pass per milestone) → Claude applies **with judgment**, and says plainly when it disagrees → Ibrahim accepts → commit.
- **Reviews.** After each milestone, run the strict reviewer agent (`.claude/agents/model-reviewer.md`): at most 2 rounds, a 3rd focused one only if needed. After that, prefer tests over more text. At major milestones, Ibrahim asks an outside reviewer (ChatGPT) for a different viewpoint: it catches what a model of the same family misses.
- **Security:** never write passwords, tokens or personal identifiers in the repo.
- **Push:** Ibrahim does `git push` himself (Claude pushes only when he asks). **Claude reminds him to commit and push** at the end of each working day, so no work is lost, and whenever a milestone (a logical step) is finished.

## 5. Next step

**See `TASKS_TODO.md`, section "Now".** It is the only place where the plan lives; do not repeat it here.
- A bug, an idea or a question comes up mid-task: add one dated line to its **Inbox**, then continue the current objective.
- When the objective is done: help Ibrahim sort the Inbox, update **Done** and `ROADMAP.md`.

Proposed repository layout (to create as needed, not all at once):
```
README.md   README.fr.md   DECISIONS.md   CLAUDE.md   .gitignore
docs/       story.md, model.md, glossary.md
sql/        schema.sql
data/       generate.py
quality/    clean.py, report.md
private/    (ignored by Git)
```
