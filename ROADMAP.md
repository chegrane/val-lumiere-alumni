# Roadmap

The big picture: the phases of the project and where we are.
Day-to-day work (current objective, bugs, ideas) is in [TASKS_TODO.md](TASKS_TODO.md). Choices and their reasons are in [DECISIONS.md](DECISIONS.md).

**Rule:** the next phase may be explored privately, but is not officially started or published until the previous one is stable.

✅ done · 🔄 in progress · ⏳ planned

## Now: the database and data quality

| Slice | Content | Status |
|---|---|---|
| Environment | PostgreSQL in Ubuntu (WSL2), Git, GitHub, [setup tutorial](docs/setup.md) | ✅ |
| 0. Framing | The story, the needs, what is out of scope, a glossary | 🔄 |
| 1. Model | Entities, class diagram, relational schema, a reason for every table and key | ⏳ |
| 2. Schema | `sql/schema.sql`: keys, constraints, indexes, views | ⏳ |
| 3. Dirty data | A generator of synthetic data with deliberate defects (duplicates, bad formats, invalid emails) | ⏳ |
| 4. Data quality | Cleaning, duplicate detection (approximate string matching), a quality report with indicators | ⏳ |
| 5. Respect for people | Consent per purpose, last verification date, deletion or anonymisation, change log, access roles | ⏳ |

## Later

| Phase | Content |
|---|---|
| Back end | An API or a Django application on top of the database |
| Front end | A management interface, then an alumni portal |
| Communication | Direct messages, announcements to all or to a group, chat |
| Community | Annual reunion and events, paid assignments (talks, mentoring, juries) |
