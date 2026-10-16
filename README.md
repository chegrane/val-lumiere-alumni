# Val-Lumière Alumni

> **Fictional institution.** Université de Val-Lumière does not exist. All names, people and data in this repository are synthetic.
> We have a university in mind, but Val-Lumière could just as well be a CEGEP, a college or any other educational institution.

An educational, open-source project: designing and building the alumni database of a fictional institution, with a strong focus on **data modelling**, **data quality** (cleaning, duplicate detection) and **respect for personal information**.

**About this project.** A personal project by Ibrahim Chegrane, built with help from two AI assistants: **Claude** (design discussions, code, first drafts) and **ChatGPT** (outside review, editing of the texts). Every design decision is his, and is recorded with its reason in [DECISIONS.md](DECISIONS.md).

**Status:** work in progress. The story and the data model are written; the SQL schema comes next ([roadmap](ROADMAP.md)).

## Documents

- [The story](docs/story.md): how we go from a human need to a well-defined project.
- [The model](docs/model.md): what we store, and how the rules are enforced.
- [The queries](docs/queries.md): how each question of the story becomes SQL, with small examples.
- [Traps and lessons](docs/lessons.md): the mistakes we really made, and what they teach.

## Setup

Requirements: **PostgreSQL** (tested with 18.6), **Git** and **Python 3** (tested with 3.14). On Windows, use Ubuntu under **WSL2** first.

```bash
sudo apt install -y postgresql                       # Ubuntu / Debian
sudo -u postgres createuser --createdb "$USER"       # your own role, no password (peer authentication)
createdb val_lumiere_alumni                          # the project database
git clone https://github.com/chegrane/val-lumiere-alumni.git ~/projects/val-lumiere-alumni
```

Then, from the project folder:

```bash
scripts/reset_db.sh                                  # build the database: schema, views, test data
python3 -m venv .venv && source .venv/bin/activate   # a private Python environment
pip install -r requirements.txt                      # pytest and psycopg
pytest                                               # run the tests
```

New to Linux, PostgreSQL or WSL? Follow the **[step-by-step tutorial](docs/setup.md)**: every command explained.

## Licence

- **Code** (`sql/`, `scripts/`, `tests/`, including the comments in those files): [MIT](LICENSE).
- **Documentation** (`docs/`, `README.md`, `README.fr.md`): [CC BY 4.0](LICENSE-DOCS). You may reuse and adapt it, including commercially, if you credit **Ibrahim Chegrane, val-lumiere-alumni**, link to the licence, and say what you changed.

*Version française : `README.fr.md` (à venir).*
