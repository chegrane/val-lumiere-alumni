# Val-Lumière Synthetic Alumni Records

*A Québec benchmark for data quality and record linkage — design notes*

**Draft v0 — October 20, 2026.** Ibrahim Chegrane, written with Claude (Anthropic) from our design discussion. Not yet built: this document describes what we intend to generate and why. Every number below is a **proposal** until the generator exists and the choice is recorded in [DECISIONS.md](../../DECISIONS.md).

> **Fictional data.** Université de Val-Lumière does not exist. The generator invents every person. It uses public statistics (name frequencies, shares of international students) only as **proportions**, never as records about real people.

---

## 1. Why this dataset

### 1.1 The need

The project [val-lumiere-alumni](../../README.md) builds the alumni database of a fictional university. Its [story](../story.md) starts from a real kind of mess: thirty years of faculty spreadsheets, a newsletter list, a reunion list, the same person two or three times under different spellings, a third of the emails dead. The database is ready (slices 0 to 2). The next question is the one the story's Director really asks: **can we clean this mess, and prove how well we did?**

To answer it, we need messy data. And to *prove* anything, we need to know the **right answer**: which rows really are the same person.

### 1.2 Why not real data

Real alumni records are personal information. In Québec, their use is framed by the law on the protection of personal information (often called "Law 25" after the 2021 reform). A public, educational project cannot use them, and should not try.

### 1.3 Why not an existing public dataset

We looked at public datasets of students (on Kaggle) and at open-source alumni systems (on GitHub). They are useful for inspiration, but none fits:

| Need | Public student datasets | What we need |
|---|---|---|
| Matches our model (degrees, contacts, consent, lists) | No: grades, finances, generic fields | Yes |
| Québec context (names, French, accents, area codes) | No | Yes |
| **Ground truth** (which rows are the same person) | **No** | **Yes**: without it, cleaning cannot be measured |
| Clear origin and licence | Varies | Yes |

Research on record linkage uses synthetic benchmarks with ground truth for the same reason; FEBRL is a well-known example (Christen, 2008). We follow their principles, adapted to French and to Québec.

### 1.4 What we want to show

- A generator whose choices are **justified by published statistics and published research**, not by guesses.
- Data realistic enough that cleaning it is genuinely hard, and **measurable**: the generator records the truth.
- Possibly, later, a **published dataset** of its own: a Québec benchmark for duplicate detection between person records, reproducible from a seed.

---

## 2. How we built it

This document comes out of a conversation between Ibrahim Chegrane and Claude, on October 20, 2026, recorded here because the *process* matters as much as the result:

1. **Start from the story**, not from the data: which files did the office really receive, from whom, in what state?
2. **Generate the truth first**: real (fictional) people, with their degrees and contacts.
3. **Then write messy copies** of them into several files, the way each source would really have produced them.
4. **Corrupt with realistic errors**, not random noise. Ibrahim's starting remark: "uniform random insertions, deletions and substitutions are blind to what people really do: someone typing O hits I or P, the neighbouring keys". This is the core of section 4.
5. **Keep the truth aside**, in files the cleaning never reads, to measure it afterwards.
6. **Justify every proportion** with an official source when one exists, and say so plainly when one does not.

**Working rule.** The dataset could become a project of its own. To keep the main project moving, **version 1 contains only what the cleaning (slice 4) needs**; every other idea goes into a backlog (section 8).

---

## 3. What is generated

### 3.1 The files

The generator writes the files the alumni office would really have received:

| File | Produced by | First row (columns) | State |
|---|---|---|---|
| `registrar_degrees.csv` | The registrar (official) | `student_number, last_name, first_name, birth_date, program, faculty, graduation_year` | **Clean**: the reference |
| `faculty_<name>_<year>.csv` (several) | Each faculty, in its own format | French headers, **different from one faculty to the next**, for example `Nom, Prénom, Matricule, Programme, Année, Courriel, Téléphone` or `NOM COMPLET; Année diplôme; Email` | **Dirty** |
| `newsletter_2019.csv` | The newsletter manager | `Courriel, Nom complet, Date d'inscription` | Medium |
| `reunion_2018.csv` | The events coordinator | `Nom, Courriel, Présent (O/N), OK pour contact` | Dirty |
| `mailing_events.csv` | The mailing system (Office 365) | `email, event, date` (`bounce` or `unsubscribe`) | Clean, but out of date relative to the lists |

**The key point for realism.** Emails and phones are **not** in the registrar's file; they are only in the messy files. So the work of slice 4 is to **link** each messy row to the right registrar person, most of the time without a student number. This is approximate matching, and it is where the difficulty lies.

### 3.2 The ground truth (never read by the cleaning)

| File | Content |
|---|---|
| `truth_people.csv` | The true people: identity, degrees, contacts, status |
| `truth_rows.csv` | For every row of every messy file: **which true person** it is, and **which defects** were applied to which fields |

With these, every cleaning step can be measured: duplicates found, missed, wrongly matched (precision and recall), and the success rate **per kind of defect**.

---

## 4. Design choices, one by one

### 4.1 Last names: Québec frequencies

**Choice.** Draw last names according to their **real frequency in Québec**.

**Why.** Frequent names produce **homonyms** (several different people named Tremblay, born the same year), which is the real difficulty of matching: two rows with the same name are not always the same person. Close names (Dion / Dionne) add near-homonyms.

**Source.** Institut de la statistique du Québec (ISQ), *Les noms de famille au Québec* (Louis Duchesne), with tables of the 1,000 most frequent names. Order of magnitude: Tremblay about 81,500 people, Gagnon 59,800, Roy 57,000, Côté 52,300, Bouchard 40,100.

**Limit.** Figures from about 2005–2006, now archived. Acceptable: the distribution of family names changes slowly. To be stated in the dataset's documentation.

### 4.2 First names: by year of birth

**Choice.** Draw each person's first name according to the names **given in Québec in the year of their birth**, and by sex.

**Why.** Popular first names change with the decades; a 1965 graduate and a 2024 graduate do not have the same names. Compound names (Marie-Ève, Jean-François) are frequent and are a major source of variants (section 4.6).

**Source.** Retraite Québec, *Banque de prénoms* (girls and boys), on Données Québec, in CSV: every first name given each year since 1980, with its count. Licence CC BY 4.0 (credit: Retraite Québec). Names given to fewer than five children are hidden ("<5").

**Limit.** The bank **starts in 1980**. Graduates of the 1990s and earlier were born in the 1960s and 1970s. Options, to decide: find an older source (the ISQ has published work on first names in Québec), or use the earliest years available as an approximation, **and say so**.

### 4.3 International students

**Choice.** A share of graduates are international students, with names from their countries of origin. The share depends on the **level of study** and on the **year**.

**Why.** Intuition from the university, confirmed by the numbers: bachelor's graduates are mostly from Québec; at master's and doctorate, international students are much more numerous. And for matching, these names bring the hardest real cases (section 4.6): transliteration (Mohamed / Mohammed / Muhammad), family name written first, several given names.

**Sources.**
- ISQ: the share of international students among graduates rose from **12.2% (2013) to 21.0% (2023)**; in 2021, **36.7% at master's** and **38.9% at doctorate**.
- Bureau de coopération interuniversitaire (BCI): about **57,000** international students in Québec universities in fall 2024, **18%** of the student population.
- Gouvernement du Québec, *Portrait statistique des étudiants internationaux*: the countries of origin. **To consult** when the generator is written.

**A strong point for later.** We can measure whether duplicate detection works **as well for every group** of names. Matching methods tuned on French names may do worse on transliterated names; measuring it is rare, and useful.

### 4.4 Dates, degrees, student numbers

| Field | Rule |
|---|---|
| Birth date | Consistent with graduation: graduating between about 21 and 35 years old |
| Degrees | From the reference lists of programs and faculties; some people get two degrees (like Karim in the test data) |
| Graduation year | From 1965 (the founding year of Val-Lumière) |
| Student number | `VL` + year of admission + a sequence number: the project's own format (uppercase letters and digits) |

### 4.5 Contact information that can never belong to anyone

| Field | Rule | Why it cannot be real |
|---|---|---|
| Email | Built from the name as people really do (`marie-eve.tremblay@…`, `metremblay@…`, `mtremblay72@…`), on domains ending in **`.example`** | `.example` is reserved for documentation and can never be a real domain (RFC 2606) |
| Phone | Real Québec area codes (819, 873, 450, 514, 418), but an **exchange starting with 0 or 1**, for example `(819) 155-2041` | In the North American Numbering Plan, the 3-digit exchange never starts with 0 or 1, so such a number is never assigned (to verify in NANPA's documents) |

**Why not the famous 555 numbers?** Only 555-0100 to 555-0199 are reserved for fiction: 100 numbers per area code, 500 in total. For thousands of people, many would share a number, and two different people sharing a phone look like duplicates: the data itself would create false clues for the matching. The exchange rule gives about 2 million numbers per area code, unique, in the right format, and impossible to dial.

### 4.6 The errors: what people really do

There are two families, with different causes, so they need different models.

#### A. Typing errors, letter by letter

**Background.** Damerau (1964) observed that most misspellings are a **single** elementary error among four: substitution, deletion, insertion, and **transposition** of two adjacent letters. Levenshtein (1966) defined the distance counting the first three; adding transposition gives the Damerau–Levenshtein distance. Pollock and Zamora (1984), studying a large corpus of errors, reported that the **first letter** of a word is rarely wrong. Kukich (1992) surveys these results. *(Exact figures to verify in the papers before publication.)*

**Model.**

| Error | Example | How it is generated |
|---|---|---|
| Substitution by a **keyboard neighbour** | Tremblay → Trwmblay (e → w) | A table: each key → its neighbouring keys. Not any letter: a neighbour |
| Transposition | Tremblay → Trmeblay | Swap two adjacent letters |
| Lost doubled letter | Pelletier → Peletier | Find a doubled letter, drop one |
| Insertion | Gagnon → Gaggnon | Repeat a letter, or insert a neighbouring key |
| Position | | Lower probability on the first letter |
| Number of errors | | Usually one per corrupted name, sometimes two |

**Keyboard layout, to decide.** In Québec the common layout is **Canadian French**, not American QWERTY, and the neighbours differ. Using the real one is more faithful; QWERTY is simpler. Whichever we choose, we say so.

#### B. Systematic variants

These are not slips of the finger, but different ways of writing the same name, or traces of the tools. In real files they are often **more frequent than typos**, and a letter-by-letter model misses them completely.

| Variant | Example | How it is generated |
|---|---|---|
| Accents lost | Marie-Ève → Marie-Eve; Lévesque → Levesque | Unicode decomposition (`unicodedata.normalize('NFD')`), then remove the accent marks |
| Hyphen, space, joined | Marie-Ève / Marie Ève / MarieEve | Replace or remove `-` |
| Case | TREMBLAY, tremblay | Upper or lower case |
| Initials, abbreviations | M. Tremblay; J.-F. Côté | Keep the first letter, add a period |
| First and last name swapped | "Tremblay Marie" | Swap the two fields |
| French phonetic variants | Thibault / Thibeault; Gauthier / Gautier; Lévesque / Lévêque | A table of rewriting rules (`ault` ↔ `eault`, `th` ↔ `t`, é / è / ê / e…) |
| Transliteration (international names) | Mohamed / Mohammed / Muhammad; Youssef / Yousef / Yusuf | A table of variant groups |
| Name change | A maiden name in an old file (like Sophie Gagnon, now Roy, in the test data) | Replace the last name in some files only |
| Encoding errors | é → Ã© ("Ã©douard") | Encode in UTF-8, decode as Windows-1252: what an old spreadsheet exported as CSV does |
| Formats | `1998-06-01` / `01/06/1998` / `juin 1998`; `819-155-2041` / `(819) 155 2041` | Several formatting functions, one drawn at random |
| Dirty emails | `gmial.example`, a missing `@`, an old address that bounces | Typos on the domain; obsolete addresses that appear in `mailing_events.csv` as bounces |

**Related work.** The GeCo generator (Christen and Vatsalan, 2013) and the generator behind FEBRL use the same families of "corruptors" (keyboard, phonetic, OCR). Our contribution is the adaptation to **French and Québec**: accents, compound first names, French phonetics, the Canadian French keyboard, and the mix of local and international names.

#### C. Record-level defects

Beyond the spelling of names: a person appears **several times** (in several files, sometimes twice in the same file); fields are **missing** (no student number in old faculty files, no birth date); an email is **out of date**; a death is **not** recorded.

### 4.7 How many errors: parameters, not hard-coded numbers

Everything is in one settings file, with a **seed**: the same seed always produces the same data, so the results and the tests are reproducible. Starting proposals, to be decided:

| Parameter | Proposal |
|---|---|
| Number of times one person appears in the messy files | 0 (35%), 1 (40%), 2 (20%), 3 or more (5%): the story's "two or three times" |
| Probability that a name has a defect | about 30% |
| Among defects | about 60% systematic variants, 40% typos |
| Typos per corrupted name | 1 (85%), 2 (15%) |
| Student number present in faculty files | 1990s: 10%; 2010s: 70% |

### 4.8 Sizes

| Size | People | Use |
|---|---|---|
| small | 2,000 | Tests and development: seconds |
| medium | 20,000 | Intermediate |
| full | **60,000** | **The story's number** |

60,000 people make the real problem appear: comparing every pair of records means about **1.8 billion** comparisons. Matching at that scale needs **blocking** (comparing only plausible candidates), a core topic of record linkage (Christen, 2012).

---

## 5. Reproducibility

- A **seed** and a **settings file** fully determine the data.
- Every source table (names, first names, shares) is stored with its **origin and date of download**.
- The generator's version is written into every output file's metadata, so a result can always be traced to the exact data it used.

---

## 6. Limits and ethics

- **Synthetic, not real.** The data imitates statistical properties; it does not describe real people. Matching quality measured on it is an estimate, not a guarantee on real files.
- **Sources have limits:** last names from about 2005; first names only since 1980; international shares by period, not by individual university.
- **Licences of the sources** must be respected and credited (Retraite Québec data: CC BY 4.0; ISQ: their terms of reuse, to check).
- **Fairness.** Names of different origins are not equally easy to match. The dataset should make this measurable, not hide it.
- **No real contact data:** reserved email domains; phone numbers that cannot exist.

---

## 7. Versions and citation

*To write when version 1 exists.* The dataset may later move to its own repository, with its own version numbers, a licence for the data, and a "how to cite" section.

---

## 8. Scope: version 1 and the backlog

**Test question for any idea:** does slice 4 (cleaning and duplicate detection) need it to work? If not, it goes into the backlog.

| Version 1 (for slice 4) | Backlog (later) |
|---|---|
| Québec last and first names (sections 4.1, 4.2) | International students and transliteration (4.3) |
| Degrees, dates, student numbers (4.4) | Encoding errors, all formats |
| Registrar file, two or three faculty files, newsletter list | Reunion list, mailing-system events |
| Typos (4.6 A) and the main systematic variants (accents, hyphens, case, initials, swaps) | French phonetics, Canadian French keyboard |
| Ground truth (3.2) | 60,000 version; fairness measures; own repository; publication |

---

## References

**Statistics and data sources**
- Institut de la statistique du Québec, *Les noms de famille au Québec* (L. Duchesne). <https://statistique.quebec.ca/fr/document/noms-de-famille-au-quebec>
- Institut de la statistique du Québec, *Noms de famille au Québec : aspects statistiques et distribution spatiale*. <https://statistique.quebec.ca/fr/document/noms-de-famille-au-quebec-aspects-statistiques-et-distribution-spatiale>
- Article citing the ISQ figures (Érudit). <https://www.erudit.org/en/culture/hq1056841/hq050/66162ac.pdf>
- Retraite Québec, *Banque de prénoms – Filles*, Données Québec (CC BY 4.0). <https://donneesquebec.ca/recherche/fr/dataset/banque-de-prenoms-filles>
- Retraite Québec, *Banque de prénoms – Garçons*, Données Québec (CC BY 4.0). <https://www.donneesquebec.ca/recherche/fr/dataset/banque-de-prenoms-garcons>
- Retraite Québec, *Banque de prénoms*. <https://www.retraitequebec.gouv.qc.ca/en/services-en-ligne-outils/banque-de-prenoms/Pages/banque-de-prenoms.aspx>
- Institut de la statistique du Québec, graduates with a bachelor's degree or higher, 2023. <https://statistique.quebec.ca/en/fichier/diplomes-baccalaureat-et-superieur-2023.pdf>
- Institut de la statistique du Québec, *En 2021, plus de femmes que d'hommes au doctorat*. <https://statistique.quebec.ca/fr/communique/2021-plus-femmes-que-hommes-doctorat>
- Bureau de coopération interuniversitaire, enrolments, fall 2024. <https://bci-qc.ca/wp-content/uploads/2024/10/Inscriptions_automne2024.pdf>
- Gouvernement du Québec, *Portrait statistique des étudiants internationaux*. <https://www.quebec.ca/education/indicateurs-statistiques/enseignement-superieur/etudes-statistiques/portrait-statistique-etudiants-internationaux>

**Contact data that cannot be real**
- D. Eastlake, A. Panitz, *Reserved Top Level DNS Names*, RFC 2606, 1999 (`.example`).
- North American Numbering Plan Administration (NANPA): numbering rules (to verify: exchanges never start with 0 or 1). <https://www.nationalnanpa.com/>
- *555 (telephone number)* and *Fictitious telephone number*, Wikipedia (the reserved range 555-0100 to 555-0199). <https://en.wikipedia.org/wiki/555_(telephone_number)>, <https://en.wikipedia.org/wiki/Fictitious_telephone_number>

**Errors and record linkage** *(to verify: exact pages and figures)*
- F. J. Damerau, "A technique for computer detection and correction of spelling errors", *Communications of the ACM*, 7(3), 1964.
- V. I. Levenshtein, "Binary codes capable of correcting deletions, insertions, and reversals", *Soviet Physics Doklady*, 10(8), 1966.
- J. J. Pollock, A. Zamora, "Automatic spelling correction in scientific and scholarly text", *Communications of the ACM*, 27(4), 1984.
- K. Kukich, "Techniques for automatically correcting words in text", *ACM Computing Surveys*, 24(4), 1992.
- I. P. Fellegi, A. B. Sunter, "A theory for record linkage", *Journal of the American Statistical Association*, 64(328), 1969.
- P. Christen, *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection*, Springer, 2012.
- P. Christen, "Febrl: an open source data cleaning, deduplication and record linkage system with a graphical user interface", KDD 2008 (demonstration).
- P. Christen, D. Vatsalan, "Flexible and extensible generation and corruption of personal data", CIKM 2013.

---

*Licence of this document: CC BY 4.0 (see [LICENSE-DOCS](../../LICENSE-DOCS)).*
