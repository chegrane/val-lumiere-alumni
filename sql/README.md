# The SQL files

Run in this order; `scripts/reset_db.sh` does it in one command, on an empty database.

| File | What it contains | Why |
|---|---|---|
| `01_schema.sql` | The 14 tables, their keys, constraints, indexes and triggers | The rules the database enforces itself ([model.md](../docs/model.md), parts 1 and 3) |
| `02_views.sql` | The four building blocks: `active_person`, `sendable_email`, `current_consent`, `recipient` | Each business rule written once; every list reads them ([queries.md](../docs/queries.md)) |
| `03_test_data.sql` | The reference lists and six people: Léa, Robert, Sophie, Karim, Nadia, Gérard | Small, hand-made data whose expected results are known: [queries.md](../docs/queries.md) says what each query must return |

Larger, realistic data (thousands of people, with deliberate defects) comes later from a generator, as CSV files (slice 3).
