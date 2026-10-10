# Val-Lumière Alumni

> **Fictional institution.** Université de Val-Lumière does not exist. All names, people and data in this repository are synthetic.
> We have a university in mind, but Val-Lumière could just as well be a CEGEP, a college or any other educational institution.

An educational, open-source project: designing and building the alumni database of a fictional institution, with a strong focus on **data modelling**, **data quality** (cleaning, duplicate detection) and **respect for personal information**.

**Status:** work in progress — the story and the data model come first.

## Documents

- [The story](docs/story.md): how we go from a human need to a well-defined project.

## Setup

Requirements: **PostgreSQL** (tested with 18.6) and **Git**. On Windows, use Ubuntu under **WSL2** first.

```bash
sudo apt install -y postgresql                       # Ubuntu / Debian
sudo -u postgres createuser --createdb "$USER"       # your own role, no password (peer authentication)
createdb val_lumiere_alumni                          # the project database
git clone https://github.com/chegrane/val-lumiere-alumni.git ~/projects/val-lumiere-alumni
```

New to Linux, PostgreSQL or WSL? Follow the **[step-by-step tutorial](docs/setup.md)**: every command explained.

*Version française : `README.fr.md` (à venir).*
