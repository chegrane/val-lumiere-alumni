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
- [x] Answer the five modelling questions (answered in `docs/story.md` and `docs/model.md`, decisions D-014 to D-026):
  - [x] Several degrees per person? Yes: `Person` 1 ── 1..* `Degree`
  - [x] Several emails per person? Which one is primary? Yes, one row per contact; one preferred per kind
  - [x] What do we keep when a person changes name? Current name on `Person`; name on the diploma on `Degree`
  - [x] "Do not contact me": one field, or consent per purpose? Consent per purpose, as a history (D-016, D-026)
  - [x] Delete a person, or anonymise and keep the statistics? De-identification plus a suppression list, honestly not anonymisation (D-019, D-022)
  - [x] How do we recognise that two records are the same person? Student number when present; otherwise approximate matching confirmed by a staff member (slice 4)
- [x] `docs/story.md`: the public story, in English (reviewed twice by a second AI)
- [x] `docs/model.md` and `docs/queries.md`: drafted by Claude, accepted by Ibrahim after a quiz, three internal review rounds and two outside reviews
- [ ] Final outside read of `docs/model.md` and `docs/queries.md` (ChatGPT)
- [ ] `docs/glossary.md`: French–English terms
- [x] Record the answers in `DECISIONS.md`, then commit

## Inbox

- 2026-10-10 — Quick cold check at the start of the next model session, **big lines only** (details stay in the files): why a person and their degrees are separate; why an internal key and not the student number; why history in the table and the current state in a view; why "stop" and "remove" are two different requests

## Next

**Slice 2 — Schema**
- [ ] `sql/schema.sql` from the model
- [ ] Decide the sort order for French names (`C.UTF-8` or a French–Canada collation)
- [ ] `Contact`: add UNIQUE (`contact_id`, `person_id`) for the two-column link from `Consent`; deletion of a contact blocked (`ON DELETE RESTRICT`), except at removal; a returning old address reactivates its `obsolete` row
- [ ] Write SQL tests from the cast and the 13 edge cases of `docs/queries.md`

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
- 2026-10-09 — The story, from the Director's request to the agreement (`7498bae`, `77fadd5`)
- 2026-10-10 — Model part 1 (store), strict reviewer agent, three review rounds (`48d60b7`, `cf70dbc`)
- 2026-10-12 — Model part 2 (queries, own file), outside reviews applied, D-022 to D-026 (`7c730ba`)
