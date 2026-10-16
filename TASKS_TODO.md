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

- 2026-10-14 — New edge case found by Ibrahim: a removed person who comes back and registers again cannot be reconnected to their anonymous row, so their old degree may be counted twice. Options: accept as a written limit (proposed for now), or pseudonymisation with a key kept by the privacy officer only. To decide

## Next

**Slice 2 — Schema**
- [x] `sql/01_schema.sql` (14 tables) and `sql/02_views.sql` (4 views) from the model
- [ ] Decide the sort order for French names (`C.UTF-8` or a French–Canada collation)
- [x] `Contact`: add UNIQUE (`contact_id`, `person_id`) for the two-column link from `Consent`; deletion of a contact blocked (`ON DELETE RESTRICT`), except at removal; a returning old address reactivates its `obsolete` row
- [x] Tests (`pytest`): the expected results on the test data and the edge cases of `docs/queries.md` (2 skipped until slice 3)
- [x] The schema's refusal tests: 26 rows that must be refused (by the right rule), 5 that must be accepted, including the NULL trap

**Before the interview (26th)**
- [ ] Read Québec privacy law for about an hour (CAI guides): consent (specific, informed, per purpose), access and correction rights, the person in charge, incident reporting

**Slice 3 — Dirty data** (Oct 20–22)
- [ ] Our own generator, not Kaggle: Faker fr_CA, CSV files, deliberate defects **with ground truth** (the generator knows which records are the same person), so cleaning can be measured
- [x] Python virtual environment, `requirements.txt` (pytest, psycopg 3); Faker and pandas to add
- [ ] Un-skip tests 13 and 14 of `tests/test_rules.py` (staging row never in a list; new degree for a listed number ignored)
- [ ] `data/generate.py`

**Slice 4 — Data quality**
- [ ] `quality/clean.py`, duplicate detection, `quality/report.md`
- [ ] Also test the duplicate detection on a standard benchmark with ground truth (FEBRL, from the Python library `recordlinkage`)

**Slice 5 — Respect for people**
- [ ] Consent, retention, deletion or anonymisation, access roles
- [ ] Rights: application roles read views, not tables; they cannot DELETE or UPDATE contacts, consents or requests directly (only `remove_person` deletes); history only grows (INSERT)
- [ ] A record of confirmation questions sent (person, kind of contact, date), so list E never asks the same person twice

**Before going public**
- [ ] Check the legal statements in `docs/story.md` (access, correction, removal, responsibility, deadlines) against the Access Act on LégisQuébec
- [ ] Licences: decide MIT for the code and **CC BY 4.0 for the texts** (story, model, queries, tutorial: anyone who reuses them must credit Ibrahim by name); add `LICENSE` (and `LICENSE-docs` if CC BY)
- [ ] Name the skill: **requirements analysis** (README and the story's subtitle)
- [ ] README, short "Related work" (2–3 lines): similar open-source alumni systems found **after** designing the model, for comparison; no code reused; what is different here (consent history, data quality, Québec law)
- [ ] `README.fr.md`
- [ ] Reread everything; make the repository public

**After slice 2 — make it a course**
- [ ] "Try it first" box before each question of `docs/queries.md` (and the key choices of `docs/model.md`): the question, a hint about which tables to look at, the trap to watch for. The reader thinks first, then reads our answer. Text work: draft by Claude, editing by ChatGPT

## Later

See [ROADMAP.md](ROADMAP.md): back end, front end, communication, community.

## Done

- 2026-10-08 — Project setup: README, `CLAUDE.md`, `.gitignore`, line endings (`bd113ca`, `27311f1`)
- 2026-10-08 — Environment: PostgreSQL 18.6 in Ubuntu (WSL2), private GitHub repository over SSH, [setup tutorial](docs/setup.md), `DECISIONS.md` (`345c378`)
- 2026-10-09 — The story, from the Director's request to the agreement (`7498bae`, `77fadd5`)
- 2026-10-10 — Model part 1 (store), strict reviewer agent, three review rounds (`48d60b7`, `cf70dbc`)
- 2026-10-12 — Model part 2 (queries, own file), outside reviews applied, D-022 to D-026 (`7c730ba`)
