# Val-Lumière Alumni

> **Fictional institution.** Université de Val-Lumière does not exist. All names, people and data in this repository are synthetic.
> We have a university in mind, but Val-Lumière could just as well be a CEGEP, a college or any other educational institution.

An educational, open-source project: designing and building the alumni database of a fictional institution, with a strong focus on **data modelling**, **data quality** (cleaning, duplicate detection) and **respect for personal information**.

**Status:** work in progress. Done: the story (requirements analysis), the data model, the PostgreSQL schema with its views, and 85 automatic tests (slices 0 to 2). Next: synthetic data with deliberate defects, then cleaning and duplicate detection ([roadmap](ROADMAP.md)).

## How this project was built

A personal project by **Ibrahim Chegrane**, built with two AI assistants, each with a clear role:

- **Claude** (Anthropic, model Claude Opus 5.5, in Claude Code): discussing and brainstorming the model; step-by-step tutorials for the technical parts (Linux, PostgreSQL, Git, Python); first drafts of the documents, SQL and tests; running the checks; and a strict reviewer agent at each milestone.
- **ChatGPT** (OpenAI, model GPT-6 Luna): an outside review at each milestone (a different viewpoint, which caught errors the other missed), and editing of the texts.

**My part:** every decision (30 so far, each recorded with its reason and the option rejected, in [DECISIONS.md](DECISIONS.md)); the story and the requirements; reading, questioning and accepting every file; running the database and the tests myself. **The rule:** nothing goes in until I understand it and can explain it.

**How we worked: slowly, hands-on first.** The project was built step by step, not generated in one go. For each part, I first thought it through myself, then we discussed it: in the model, the "first idea" behind each choice is usually mine, followed by the problem it causes and the solution kept. I created and broke the first table by hand in `psql`, wrote a first version of two tables (`person`, `degree`) before Claude completed them, ran every command of the setup, the database and the tests myself, and answered short quizzes to check that I could explain the main choices without notes. Claude wrote most of the final SQL and the tests; I read, questioned and accepted each file.

Commits written with Claude carry the line `Co-Authored-By: Claude`.

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
