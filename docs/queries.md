# The queries

**Goal of this file:** show that the [model](model.md) answers every question of the [story](story.md), and how we go from a question in plain English to its SQL.

This is part 2 of the model, **Compute**. Part 1 (what we store) and part 3 (how rules are enforced) are in [model.md](model.md).

> **Draft SQL.** The code shows the logic; it is tested in slice 2, once the tables exist. Table names are the class names in lowercase with `_` (`contact_purpose`, `do_not_contact`…), to be confirmed in slice 2.

---

## How to read this file

Each question follows the same five steps:

1. **The question**, in plain words.
2. **A small example**, with people from the cast below.
3. **The rule**, in plain words, and why it works.
4. **The SQL**, with a short explanation.
5. **The result**, on the cast, and the one thing to remember.

Difficult questions get all five steps. Simpler ones are shorter.

---

## Can we reach them, and may we contact them?

Before preparing any mailing list, we must answer **two different questions**.

**1. Can we reach the person?**
The person is alive, has not been removed, and has an email address we can reasonably try. This is about the **quality of our contact information**.

**2. May we contact the person?**
The person has agreed to receive **this kind** of message: newsletter, event invitation or assignment offer. This is about **their choice**.

A person can pass one test and fail the other:

| Person | Can we reach them? | May we contact them? | What do we do? |
|---|---|---|---|
| Robert | Yes: his email is valid | No: he asked us to stop | Do not send |
| Sophie | No: her email bounced | Yes: she agreed | Do not send; find her new address |
| Nadia | Yes: her work email is valid | Yes, for assignment offers only | Send offers, not the newsletter |

**A mailing list needs both answers to be yes.** Having an email address does not give us permission to use it. Having permission does not mean the address still works.

The two gaps are two different problems, for two different people in the office: Sophie's is a **data quality** problem (find her new address); Robert's is a **respect** problem (never send, even though we could).

In the queries below, four small building blocks carry these rules, so that no list has to repeat them:

| Building block | Answers |
|---|---|
| `active_person` | Is the person alive and not removed? |
| `sendable_email` | Which of their emails can we try? (**can**) |
| `current_consent` | What is their usable answer today, for each kind of message, if they have one? (**may**) |
| `recipient` | Who receives what, at which address? (**can and may**) |

---

## The cast

Six people, used in every example. In slice 2, they become the test data.

| Person | Degrees (faculty at graduation, field, year) | Emails | Consent history |
|---|---|---|---|
| **Léa** | Science, Computer science, 2024 | personal: valid, preferred · university: obsolete | newsletter yes, events yes |
| **Robert** | Administration, Management, 1995 | personal: valid, preferred | "Newsletter sign-ups 2019" (an imported list, documented by the sign-up forms): yes · 2024-05-10, by phone: **no** to everything |
| **Sophie** | Education, Education, 2009 | personal: **bounced** | newsletter yes, events yes |
| **Karim** | Science, Mathematics, 1998 · Engineering, Civil engineering, 2012 | personal: **unknown** (never checked), preferred | events yes · newsletter: yes on 2026-01-15, then **unsubscribe link** on 2026-03-02 |
| **Nadia** | Engineering, Civil engineering, 2003 · expertise: Civil engineering | work: valid, preferred | offers yes |
| **Gérard** | Engineering, Civil engineering, 1995 (old spreadsheet) | none | none: never asked |

**Totals:** 6 people, 7 degrees (Karim has two).

---

## The building blocks

### `current_consent` — what is the person's answer today?

**The question.** For each person and each kind of message (newsletter, events, offers): do we have a **usable** answer today, and is it yes or no?

**Small examples.**
- Karim said "yes" to the newsletter on January 15, 2026. On March 2, he clicked the unsubscribe link at the bottom of a newsletter; Office 365 sent us that action, with its date. His answer today: **no**.
- Robert is in the imported list "Newsletter sign-ups 2019" with "yes". On May 10, 2024, he called to say "stop". His answer today: **no**.
- Imagine an old mailing system that never recorded Robert's stop, and sends us a list on March 10 that still says "yes". That list must **not** make him contactable again.
- Imagine a 1995 reunion spreadsheet with a column "OK to contact: yes". Nobody knows what people were told, or for what. That "yes" proves nothing.

**Where answers come from.** An answer either is **the person's own choice**, with its real date (typed by the staff, or an individual action such as an unsubscribe click), or comes from an **imported list**: a snapshot saying what was true, not when anyone chose. Each imported answer points to its list (`SourceList`, [model.md](model.md)), which records when we received it and whether it proves consent for its kind of message.

**The rule** ([D-026](../DECISIONS.md#d-026--consent-three-kinds-of-evidence-2026-10-12)). Not all answers are equally strong. There are three kinds of evidence:

| Kind of evidence | Counts… |
|---|---|
| **The person's own choice**, with its real date | from the day of the choice |
| **A "no" from a list** | from the day we **received** the list: it blocks, until the person chooses again later |
| **A "yes" from a list** | only when there is nothing else, and only if the list proves consent for that kind of message (the newsletter sign-up forms do; the reunion spreadsheet does not) |

Then: **the latest wins, and on the same day, "no" wins.** In one sentence: *an old "yes" can never cancel a "no", and a "yes" we cannot justify is not enough to send.*

**No row is not "no".** The view returns the **usable** answer, when one exists. A person with no row has no usable answer: either they were never asked (Gérard), or their only "yes" comes from a list that proves nothing. Either way, nothing is sent. List E finds the second case, so the office can ask them.

**The SQL.** Each answer receives a **sort date** that expresses the rule; then we keep the first answer of each person and kind.

```sql
CREATE VIEW current_consent AS
SELECT DISTINCT ON (person_id, purpose_id)
       person_id, purpose_id, granted, counts_from, channel, entry, source_list_id, contact_id
FROM (
    SELECT c.*,
           CASE
             WHEN c.entry = 'file import' AND NOT c.granted
                  THEN (sl.received_at AT TIME ZONE 'America/Montreal')::date
                                                 -- a list's "no": from the day we received the list
             WHEN c.entry = 'file import'
                  THEN '-infinity'::date         -- a list's "yes": only if there is nothing else
             ELSE c.given_on                     -- the person's own choice: its real date
           END AS counts_from
    FROM consent c
    LEFT JOIN source_list sl ON sl.source_list_id = c.source_list_id
    WHERE NOT (c.entry = 'file import'
               AND c.granted
               AND NOT sl.documented)            -- a "yes" from a list that proves nothing is set aside
) AS c
ORDER BY person_id, purpose_id,
         counts_from DESC,     -- the latest first
         granted,              -- same day: "no" (false) before "yes"
         recorded_at DESC,     -- still tied: the last one recorded
         consent_id DESC;      -- and a final tie-breaker, so the choice never changes
```

- The inner query gives each answer its `counts_from` date. **It asks "does this answer come from a list?" first**: a list's answer never uses a choice date (and the model keeps `given_on` empty for list answers anyway). A first version asked about the date first, and a dated list "yes" could beat a "no": that was a bug.
- `LEFT JOIN source_list` brings the list's reception date and its proof status; answers that are not from a list simply have no list.
- `AT TIME ZONE 'America/Montreal'` gives the **office's** calendar day. Without it, the day would depend on the connection's time zone: a list received at 22:30 in Montréal is already the next day in UTC.
- `'-infinity'` is a PostgreSQL date older than every other date: a list's "yes" can only win if nothing else exists. It is how the rule is implemented, not the rule itself.
- The `WHERE` sets aside the "yes" answers from lists that prove nothing.
- `ORDER BY` puts the answer that should win first; `DISTINCT ON (person_id, purpose_id)` keeps only that one, for each person and kind of message.

**The result.** Robert: no, no, no. Karim: newsletter **no**, events yes. Gérard: **no row**: no usable answer, so no message.

### `active_person` — alive and not removed

**The rule.** A person with a reported death, or whose information was removed, is never contacted, for anything. Written once, here, it protects every list. This is where the story's painful mistake (an invitation sent to a deceased graduate) is prevented.

```sql
CREATE VIEW active_person AS
SELECT *
FROM person
WHERE deceased_reported_on IS NULL
  AND removed_on IS NULL;
```

**The result.** All six are active.

### `sendable_email` — which emails can we try? (*can*)

**A small example.** Léa has two emails: her personal one works; her university one is `obsolete` (she stopped reading it). Karim's email has never been checked: its status is `unknown`. Sophie's only email bounced.

**The rule.** An email is `valid` when a message to it was delivered, or the person confirmed it; `unknown` when neither has happened yet. An email is *sendable* when it belongs to an active person and is `valid` or `unknown`. We include `unknown` on purpose: most addresses are never formally checked, and an address that was never shown to fail is worth trying. That is why the view is called *sendable* and not *working*: it means "we may try", not "it works".

```sql
CREATE VIEW sendable_email AS
SELECT c.contact_id, c.person_id, c.value AS email, c.status, c.is_preferred
FROM contact c
JOIN active_person p ON p.person_id = c.person_id
WHERE c.kind = 'email'
  AND c.status IN ('valid', 'unknown');
```

**The result.** Léa (personal), Robert, Karim (`unknown`), Nadia. Not Sophie, not Léa's university email, not Gérard.

### `recipient` — who receives what, at which address? (*can and may*)

**A small example.** Nadia agreed to assignment offers only: she receives offers, at her work email, and nothing else. Robert has a valid email but said no: he receives nothing. Sophie said yes but her email bounced: she receives nothing, and her case goes to the staff.

**The rule.** Keep only the people who **pass both tests**: they agreed to this kind of message (*may*), **and** they have a sendable email (*can*). Which email? The one they chose for this kind of message, if any; otherwise their preferred email. If the chosen email no longer works, we do not send: Léa said "only my personal email", and another address would go against her choice.

```sql
CREATE VIEW recipient AS
SELECT cc.person_id, cc.purpose_id, se.email
FROM current_consent cc
JOIN sendable_email se
  ON se.person_id = cc.person_id
 AND (   se.contact_id = cc.contact_id                     -- the email chosen for this kind
      OR (cc.contact_id IS NULL AND se.is_preferred))      -- otherwise the preferred email
WHERE cc.granted;
```

- `WHERE cc.granted` keeps only the "yes" answers (*may*).
- The `JOIN` keeps a person only if a sendable email matches (*can*). A person who fails either test simply does not appear.
- If the chosen email is no longer sendable, the join finds nothing: not sent, as decided.
- A person with sendable emails but **none preferred and none chosen** is not in the list either. That is on purpose: we do not guess which address to use. The staff are alerted to ask.

**The result.** Léa (newsletter, events), Karim (events only, since he unsubscribed from the newsletter), Nadia (offers).

---

## Statistics

### Q1 — How many graduates do we have, by faculty and by year?

**The question.** The story asks for totals by faculty and by year. But "graduates" can mean two things: **people** or **degrees**.

**A small example.** Karim has a degree in Science (1998) and one in Engineering (2012).
- Counting **degrees**: Science 2, Engineering 3, Administration 1, Education 1 → **7**. Correct.
- Counting **people**: Science 2 (Léa, Karim), Engineering 3 (Karim, Nadia, Gérard), Administration 1, Education 1. Add them up: 7. But we have **6** people. Karim is in two faculties, so he is counted in both.

**The rule.**
- Count **both**: people and degrees. The story asks for both.
- **Never add the faculty totals of people** to get the number of graduates. The sum is larger, because some people graduated from more than one faculty. The report must say so.
- To count people inside a group, count each person **once**, even if they have two degrees in that group.
- Use the faculty **at graduation**, stored on each degree ([D-025](../DECISIONS.md#d-025--faculty-at-graduation-stored-on-each-degree-2026-10-12)). If a program moves to another faculty later, the past does not change.
- Removed people are counted: their degrees are kept for this reason (without their names).

**The SQL.** One query gives every level at once: by faculty and year, by faculty, by year, and the overall total.

```sql
SELECT f.name                               AS faculty,
       d.graduation_year                    AS year,
       COUNT(DISTINCT d.person_id)          AS people,
       COUNT(*)                             AS degrees,
       GROUPING(f.name, d.graduation_year)  AS level
FROM degree d
JOIN faculty f ON f.faculty_id = d.faculty_id
GROUP BY CUBE (f.name, d.graduation_year)
ORDER BY level, faculty, year;
```

- `COUNT(*)` counts rows, which are degrees. `COUNT(DISTINCT d.person_id)` counts each person once in each group.
- `GROUP BY CUBE (faculty, year)` computes every combination in one pass. In the result, an empty faculty or year means "all".
- `GROUPING(…)` labels each row: 0 = faculty and year, 1 = by faculty, 2 = by year, 3 = overall total. A chart keeps only the rows of the level it shows.

**The result.** Overall total: 6 people, 7 degrees. By faculty: Science 2 people, Engineering 3, Administration 1, Education 1.

**Stored or computed each time?** This is the heaviest query, and totals a few hours old harm no one. It is a good candidate for a **materialized view** (a stored result, refreshed at night). Consent, by contrast, must always be fresh: Robert's "stop" must count at once. So `current_consent` stays a plain view.

**To remember:** a person and a degree are not the same thing to count.

### Q2 — How many people can we reach today?

**The question.** How many living, non-removed graduates have at least one email the office can try? We are **not** asking yet whether they agreed to receive a message.

**A small example.**
- Robert has a valid email, but asked us to stop. He **counts** here: we have a usable address. He will appear on no mailing list, because his answer is "no".
- Sophie agreed to receive messages, but her only email bounced. She **does not count**: her case needs the office's attention.
- Karim's email has never been checked (`unknown`). He counts as *potentially* reachable, not as having a *valid* email.

**The rule.** Start from active people, and count each person **once** (Léa has two emails). Report two measures:
- **potentially reachable:** at least one email `valid` or `unknown`, which the office may try;
- **with a valid email:** at least one email `valid` (a message was delivered, or the person confirmed it).

**The SQL.**

```sql
SELECT (SELECT COUNT(*) FROM active_person)                       AS active_people,
       (SELECT COUNT(DISTINCT person_id) FROM sendable_email)     AS potentially_reachable,
       (SELECT COUNT(DISTINCT person_id) FROM sendable_email
         WHERE status = 'valid')                                  AS with_valid_email;
```

**The result.** 6 active people; 4 potentially reachable (Léa, Robert, Karim, Nadia); 3 with a valid email (Léa, Robert, Nadia).

**To remember:** the two people we cannot reach (Sophie, Gérard) are a **contact data** problem. Robert is a different problem: we *can* reach him, but we *may not*. That is why reachability and consent are calculated separately.

---

## The lists

The building blocks do the hard work. Each list only chooses the kind of message and, sometimes, who is targeted.

### List A — Who receives the newsletter, at which email?

```sql
SELECT r.person_id, r.email
FROM recipient r
JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
WHERE cp.name = 'newsletter';
```

**The result.** Léa only. Karim unsubscribed, Robert said no, Sophie's email bounced, Nadia did not ask for it, Gérard was never asked. This is the list given to Office 365.

### Q3 — Whom do we invite to this year's reunion?

**The rule.** Everyone who agreed to event invitations and has a sendable email, **one invitation per person**, even with two degrees.

```sql
SELECT r.person_id, r.email
FROM recipient r
JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
WHERE cp.name = 'events';
```

**The result.** Léa and Karim, once each. Karim has two degrees, but `recipient` does not look at degrees: one row per person and kind of message. Sophie agreed but cannot be reached: she goes on the office's "find a new address" list.

### List B — A department event: Mathematics graduates of 1995 to 2000

**A small example.** Imagine Karim had two Mathematics degrees in those years. A naive query that joins people with their degrees would give **one row per degree**: Karim would be invited twice.

**The rule.** Keep a person if **there exists** at least one degree in the field and the years, and list each person once.

```sql
SELECT r.person_id, r.email
FROM recipient r
JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
WHERE cp.name = 'events'
  AND EXISTS (
        SELECT 1
        FROM degree d
        JOIN program p ON p.program_id = d.program_id
        JOIN field   f ON f.field_id   = p.field_id
        WHERE d.person_id = r.person_id
          AND f.name = 'Mathematics'
          AND d.graduation_year BETWEEN 1995 AND 2000);
```

- `EXISTS (…)` answers yes or no for each person, so each person appears once, however many degrees match.
- This uses the program's field. The model assumes a program's field does not change (unlike its faculty, which is stored at graduation).
- The field and the years are written in the query. A view cannot take parameters; if this kind of list is prepared often, a SQL function can come later.

**The result.** Karim (Mathematics, 1998).

### Q4 — Which engineering graduates agreed to receive assignment offers?

**The question.** The story says *engineering graduates*: people with at least one degree from the **Faculty of Engineering**. That is a faculty, not a field: civil, mechanical or software engineering all count.

**The rule.** People who agreed to assignment offers and have a sendable email (`recipient`), **and** who have at least one degree from the Faculty of Engineering, using the faculty **at graduation**.

```sql
SELECT r.person_id, r.email
FROM recipient r
JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
WHERE cp.name = 'assignment offers'
  AND EXISTS (
        SELECT 1
        FROM degree  d
        JOIN faculty f ON f.faculty_id = d.faculty_id
        WHERE d.person_id = r.person_id
          AND f.name = 'Engineering');
```

**The result.** Nadia. Karim has an engineering degree but did not agree to offers; Gérard was never asked.

### List C — An assignment offer in civil engineering

**A small example.** An offer is often more precise than a faculty. Nadia studied civil engineering, and she also declared it as her expertise after 20 years in industry. Someone could have the expertise without the degree.

**The rule.** People who agreed to offers, **and** who studied in the field **or** declared an expertise in it.

```sql
SELECT r.person_id, r.email
FROM recipient r
JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
WHERE cp.name = 'assignment offers'
  AND (   EXISTS (SELECT 1
                  FROM degree d
                  JOIN program p ON p.program_id = d.program_id
                  JOIN field   f ON f.field_id   = p.field_id
                  WHERE d.person_id = r.person_id
                    AND f.name = 'Civil engineering')
       OR EXISTS (SELECT 1
                  FROM person_expertise pe
                  JOIN field f ON f.field_id = pe.field_id
                  WHERE pe.person_id = r.person_id
                    AND f.name = 'Civil engineering'));
```

**The result.** Nadia. Not Karim (civil engineering degree, but no consent for offers), not Gérard (never asked, no email).

---

## One person

### Q5 — When was this person's contact information last checked?

```sql
SELECT kind, label, value, status, last_checked_on, status_changed_on
FROM contact
WHERE person_id = 48213
ORDER BY last_checked_on DESC NULLS LAST;
```

All of the person's contacts, the most recently checked first; never-checked ones at the end (`NULLS LAST`). `48213` stands for the person's `person_id`.

### Q6 — Who asked not to be contacted, for what, and since when?

**A small example.** Robert said "no" to everything on May 10, 2024, by phone. Karim said "no" to the newsletter on March 2, 2026, with an unsubscribe link. Gérard was **never asked**: he did not refuse anything. And imagine an imported list where someone is marked "no": we block contact from the day we received it, but the list does not tell us when, or even whether, that person asked.

**The rule.** The story asks *who asked*. Only the person's own "no" answers that. Three results, clearly labelled:
- **Refusals expressed by the person:** a current "no" that is their own choice (typed by the staff, or an action such as an unsubscribe click). This answers the story's question.
- **Blocks from imported lists:** a current "no" that comes from a list. We respect it, but it is a protective block, not proof of when or how the person refused.
- **Suppression list entries:** student numbers kept after a removal. Not all of them are refusals either: the reason may be a stop request, a reported death, or a removal.

```sql
-- Refusals expressed by the person
SELECT p.person_id, p.last_name, cp.name AS purpose, cc.counts_from, cc.channel
FROM current_consent cc
JOIN active_person   p  ON p.person_id   = cc.person_id
JOIN contact_purpose cp ON cp.purpose_id = cc.purpose_id
WHERE NOT cc.granted
  AND cc.entry <> 'file import'
ORDER BY cc.counts_from;

-- Blocks from imported lists
SELECT p.person_id, p.last_name, cp.name AS purpose, sl.name AS list, sl.received_at
FROM current_consent cc
JOIN active_person   p  ON p.person_id      = cc.person_id
JOIN contact_purpose cp ON cp.purpose_id    = cc.purpose_id
JOIN source_list     sl ON sl.source_list_id = cc.source_list_id
WHERE NOT cc.granted
ORDER BY sl.received_at;

-- Suppression list entries
SELECT student_number, reason, since
FROM do_not_contact
ORDER BY since;
```

**The result.** Refusals expressed by the person: Robert (newsletter, events, offers; 2024-05-10; phone) and Karim (newsletter; 2026-03-02; unsubscribe link). No blocks from lists in the cast. Not Gérard. On the suppression list, `since` is the date of the reason kept: the death report, the stop request, or the removal.

### Q8 — "What do you know about me?"

**The question.** A graduate asks what we hold about them. The answer must be complete: their person record, degrees, contacts, the **whole** consent history (not only today's answer), requests, event registrations and expertise.

**A small example.** Imagine a person with 3 contacts and 5 consent answers. One big join of all these tables gives 3 × 5 = 15 lines, each contact repeated 5 times, each answer repeated 3 times. Nobody could read that.

**The rule.** One query per class that points to a person, all filtered on the same person.

```sql
SELECT * FROM person            WHERE person_id = 48213;
SELECT * FROM degree            WHERE person_id = 48213;
SELECT * FROM contact           WHERE person_id = 48213;
SELECT * FROM consent           WHERE person_id = 48213
         ORDER BY COALESCE(given_on, recorded_at::date);
SELECT * FROM request           WHERE person_id = 48213 ORDER BY received_on;
SELECT * FROM registration      WHERE person_id = 48213;
SELECT * FROM person_expertise  WHERE person_id = 48213;
```

For imported answers, the report also names the list each one came from (`source_list`), so the person can see where we got it.

**Limits.** These queries gather the raw data. A real answer to the person is a readable document: the application must assemble it, and replace identifiers by names (the program's name, not `program_id = 12`). It covers **this database only**; other systems (Office 365, archives) need their own search. A test in part 3 checks that every class with a `person_id` is in this list, so that a class added later is not forgotten.

### Q9 — A removal: done, verified, totals unchanged

**The question.** A graduate asks us to remove their information. Did we do everything we promised, and did the statistics stay the same?

**Two different things.**
- **Doing it** changes the data: the steps of [model.md, 1.4](model.md#14-removal). They run as **one transaction**: everything is done, or nothing. This is written in slice 2.
- **Verifying it** reads the data and looks for mistakes. That is the query below.

**The rule.** A **check query** lists the removed people who still have something that should be gone. **Its correct answer is empty.** One row means a mistake.

```sql
SELECT p.person_id
FROM person p
WHERE p.removed_on IS NOT NULL
  AND (   p.first_name           IS NOT NULL
       OR p.last_name            IS NOT NULL
       OR p.student_number       IS NOT NULL
       OR p.birth_date           IS NOT NULL
       OR p.deceased_reported_on IS NOT NULL
       OR p.deceased_source      IS NOT NULL
       OR EXISTS (SELECT 1 FROM contact          c  WHERE c.person_id  = p.person_id)
       OR EXISTS (SELECT 1 FROM consent          cs WHERE cs.person_id = p.person_id)
       OR EXISTS (SELECT 1 FROM registration     r  WHERE r.person_id  = p.person_id)
       OR EXISTS (SELECT 1 FROM person_expertise pe WHERE pe.person_id = p.person_id)
       OR EXISTS (SELECT 1 FROM request          rq WHERE rq.person_id = p.person_id)
       OR EXISTS (SELECT 1 FROM degree d
                  WHERE d.person_id = p.person_id
                    AND (   d.name_at_graduation IS NOT NULL
                         OR d.source NOT IN ('registrar', 'spreadsheet'))));
```

**The totals.** Run Q1 before and after the removal: the degree counts must be identical.

**The trace.** The `remove` request stays, detached from the person, with `outcome = 'done'`, its dates and who handled it.

**Limits.** This query verifies the rules written in the model, **in this database**. It does not prove that the person is gone from the archived spreadsheets or from other systems, and it does not make the kept data anonymous ([model.md, 1.4](model.md#14-removal)).

**To remember:** changing the data and verifying the change are two separate steps. A check query whose correct answer is empty is the simplest kind of test.

---

## Requests

### List D — Open requests, and the deadlines

**The rule.** Not every request has a legal deadline.
- **Access and correction** requests (in writing): the law gives 20 days, extendable by 10 (simplified here).
- **Stop** and **remove** requests: the office's own target. "Stop" is applied right away; removal follows the office's procedure.

```sql
SELECT request_id, type, received_on,
       CASE WHEN type IN ('access', 'correction')
            THEN received_on + 20
       END                         AS legal_deadline,
       current_date - received_on  AS days_open
FROM request
WHERE handled_on IS NULL
ORDER BY received_on;
```

- In PostgreSQL, a date plus a whole number is a date, and a date minus a date is a number of days.
- `legal_deadline` is empty for `stop` and `remove`: they follow the office's targets, not the access law.
- Late access or correction requests only: add `AND type IN ('access', 'correction') AND received_on + 20 < current_date`.

### List E — Answers to confirm

**The rule.** People whose only "yes" for a kind of message comes from a list that proves nothing: they have no usable answer. The office asks them to confirm, once, for that kind of message.

```sql
SELECT DISTINCT c.person_id, cp.name AS purpose, sl.name AS list
FROM consent c
JOIN active_person   p  ON p.person_id      = c.person_id
JOIN contact_purpose cp ON cp.purpose_id    = c.purpose_id
JOIN source_list     sl ON sl.source_list_id = c.source_list_id
WHERE c.granted
  AND NOT sl.documented
  AND NOT EXISTS (SELECT 1 FROM current_consent cc
                  WHERE cc.person_id  = c.person_id
                    AND cc.purpose_id = c.purpose_id);
```

- `NOT EXISTS` keeps only the people with no usable answer for that kind: if they already said yes or no themselves, or a list blocks them, there is nothing to ask.
- **Proof found later.** If the office later finds the forms behind a list, it records the proof **on the list** (where it is, when and by whom it was checked). The list becomes documented; its "yes" answers count from then on, and they leave list E. No answer is rewritten.

---

## Edge cases to test

Each case is dated, with its expected result. In slice 2, each becomes a test.

| # | Case | Expected |
|---|---|---|
| 1 | Robert: list "Newsletter sign-ups 2019" (documented) says yes; 2024-05-10 by phone: no | Current newsletter answer: **no** |
| 2 | Karim: 2026-01-15 yes to the newsletter; 2026-03-02 unsubscribe link (through Office 365) | **No**; not in list A |
| 3 | A person says "stop" on 2026-03-02; an old system's list, received 2026-03-10, still says "yes" | **No**: a list's "yes" never cancels a "no" |
| 4 | A list says "no", received 2026-04-01; the person had said "yes" directly in 2025 | **No**, from 2026-04-01 |
| 5 | Same person, then on 2026-06-01 they write: "yes, I want the newsletter again" | **Yes**: a later choice by the person lifts the block |
| 6 | Only a "yes" from the 1995 reunion spreadsheet (undocumented) | **No row** (no usable answer): not sent; in list E |
| 7 | Same as 6, then the office finds the forms and documents the list | **Yes**; out of list E; no consent row changed |
| 8 | Only a "yes" from a documented sign-up list | **Yes** |
| 9 | A documented newsletter list, used for assignment offers | **Refused by the database**: a list is about one kind of contact only |
| 10 | An answer from a list that carries a choice date | **Refused by the database**: a list snapshot never carries a choice date |
| 11 | A "yes" and a "no" from the person, same day | **No** |
| 12 | Karim's email is `unknown` | Potentially reachable, no valid email; still invited to the reunion |
| 13 | A staging row "M. Tremblay, 1995", identity not confirmed | In **no** list; never in `person` until confirmed |
| 14 | Paul (a separate scenario) is removed in 2025; in 2026 the registrar sends a new degree with his student number | The degree is **ignored**; the degree total misses it (accepted limit) |
| 15 | After Paul's removal | Q9's check query is **empty**; Q1's degree totals are unchanged |
| 16 | An access request received by phone | **Refused by the database**: an access request must be in writing |

---

## Left for slice 4

- **Q7 — Who appears more than once?** Needs approximate matching on names, birth dates and degrees: the duplicate detection of slice 4. It will read `person` and `degree`, and propose pairs for a staff member to confirm.
- **Q10 — Better or worse, month after month?** Needs dated measurements (share of `bounced`, of `unknown`, of people with no sendable email…), stored each month by the quality process.

---

## What this part taught us

- **Every question has an answer** with the classes of the model. Q7 and Q10 need the tools of slice 4, as planned.
- **Four building blocks** carry the rules once: `active_person`, `sendable_email`, `current_consent`, `recipient`. Every list reads them.
- **Can and may are two tests.** A list needs both. The people who fail one test are not the same problem as those who fail the other.
- **People are not degrees.** Count both, and never add faculty totals of people.
- **Plain view for consent** (always fresh); **materialized view for statistics** (heavy, a few hours old is fine).
- **One row per person:** use `EXISTS`, not a join with degrees, when a list targets people.
