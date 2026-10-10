# Tasks to do

Everything actionable: the current objective, what comes up along the way, what is next, what is done.
The big picture is in [ROADMAP.md](ROADMAP.md).

**How this file works**
1. **Now** holds one objective only.
2. A bug, an idea or a question comes up while working? One line in **Inbox**, with the date, then back to the objective.
3. When the objective is done: sort the Inbox (move each line to Next or Later, or delete it), then choose the next objective.
4. **Done** keeps milestones and their commits only; Git keeps the detailed history.

## Now — Slice 0–1: framing and model (no code)

- [x] Reread the story (draft: `private/projet_diplomes_brief.md`, section 3)
- [ ] Answer the five modelling questions (section 6 of the same brief):
  - [ ] Several degrees per person?
  - [ ] Several emails per person? Which one is primary?
  - [ ] What do we keep when a person changes name?
  - [ ] "Do not contact me": one field, or consent per purpose?
  - [ ] Delete a person, or anonymise and keep the statistics?
  - [ ] How do we recognise that two records are the same person?
- [x] `docs/story.md`: the public story, in English (reviewed twice by a second AI)
- [ ] `docs/model.md`: entities and attributes, **written by Ibrahim**
- [ ] `docs/glossary.md`: French–English terms
- [ ] Record the answers in `DECISIONS.md`, then commit

## Inbox

- 2026-10-08 — README: add the sentence "personal project, built with help from an AI assistant for part of the code"
- 2026-10-08 — `.gitignore`: comments are in French; translate to English (language rule)
- 2026-10-08 — Create the strict reviewer agent (`.claude/agents/`) and write the review loop rule (max 2–3 rounds) in `CLAUDE.md`
- 2026-10-08 — `CLAUDE.md`: soften the 1 h 30 block rule (remind once, then follow Ibrahim's choice)

## Next

**Slice 2 — Schema**
- [ ] `sql/schema.sql` from the model
- [ ] Decide the sort order for French names (`C.UTF-8` or a French–Canada collation)

**Slice 3 — Dirty data**
- [ ] Python virtual environment; install Faker, pandas, psycopg 3
- [ ] `data/generate.py`

**Slice 4 — Data quality**
- [ ] `quality/clean.py`, duplicate detection, `quality/report.md`

**Slice 5 — Respect for people**
- [ ] Consent, retention, deletion or anonymisation, access roles

**Before going public**
- [ ] Check the legal statements in `docs/story.md` (access, correction, removal, responsibility, deadlines) against the Access Act on LégisQuébec
- [ ] Confirm the licence (MIT proposed) and add `LICENSE`
- [ ] `README.fr.md`
- [ ] Reread everything; make the repository public

## Later

See [ROADMAP.md](ROADMAP.md): back end, front end, communication, community.

## Done

- 2026-10-08 — Project setup: README, `CLAUDE.md`, `.gitignore`, line endings (`bd113ca`, `27311f1`)
- 2026-10-08 — Environment: PostgreSQL 18.6 in Ubuntu (WSL2), private GitHub repository over SSH, [setup tutorial](docs/setup.md), `DECISIONS.md` (`345c378`)
