"""Small helpers shared by the tests, so each test reads like its scenario.

Every value is passed as a PARAMETER (%s), never pasted into the SQL text.
"""


def fetch_all(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


def fetch_one(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()


def person_id(cur, first_name):
    return fetch_one(cur, "SELECT person_id FROM person WHERE first_name = %s", (first_name,))[0]


def contact_id(cur, email):
    return fetch_one(cur, "SELECT contact_id FROM contact WHERE value = %s", (email,))[0]


def recipients(cur, purpose):
    """First names of the people who receive this kind of message (the view recipient)."""
    rows = fetch_all(
        cur,
        """SELECT p.first_name
           FROM recipient r
           JOIN person p USING (person_id)
           JOIN contact_purpose cp USING (purpose_id)
           WHERE cp.name = %s""",
        (purpose,),
    )
    return sorted(row[0] for row in rows)


def current_answer(cur, first_name, purpose):
    """(granted, entry, counts_from) from current_consent, or None if there is no usable answer."""
    return fetch_one(
        cur,
        """SELECT cc.granted, cc.entry, cc.counts_from
           FROM current_consent cc
           JOIN person p USING (person_id)
           JOIN contact_purpose cp USING (purpose_id)
           WHERE p.first_name = %s AND cp.name = %s""",
        (first_name, purpose),
    )


def add_own_answer(cur, first_name, purpose, granted, given_on,
                   channel="email", entry="staff", contact=None):
    """The person's own choice, with its real date."""
    cur.execute(
        """INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry,
                                recorded_by, contact_id)
           SELECT p.person_id, cp.purpose_id, %s, %s, %s, %s, 'test', %s
           FROM person p, contact_purpose cp
           WHERE p.first_name = %s AND cp.name = %s""",
        (granted, given_on, channel, entry, contact, first_name, purpose),
    )


def add_list(cur, name, purpose, received_at, documented=False):
    """An imported list, for one kind of contact. Returns its id."""
    evidence = ("test forms", "2026-01-01", "test") if documented else (None, None, None)
    return fetch_one(
        cur,
        """INSERT INTO source_list (name, purpose_id, received_at, documented,
                                    evidence_ref, evidence_checked_on, evidence_checked_by)
           SELECT %s, purpose_id, %s, %s, %s, %s, %s
           FROM contact_purpose WHERE name = %s
           RETURNING source_list_id""",
        (name, received_at, documented, *evidence, purpose),
    )[0]


def add_list_answer(cur, first_name, list_id, granted):
    """An answer coming from an imported list (a snapshot: no choice date)."""
    cur.execute(
        """INSERT INTO consent (person_id, purpose_id, granted, channel, entry,
                                source_list_id, recorded_by)
           SELECT p.person_id, sl.purpose_id, %s, 'unknown', 'file import', sl.source_list_id, 'test'
           FROM person p, source_list sl
           WHERE p.first_name = %s AND sl.source_list_id = %s""",
        (granted, first_name, list_id),
    )


# Q9 of docs/queries.md: the removed people who still have something that should be gone.
# Its correct answer is EMPTY.
REMOVAL_CHECK = """
    SELECT p.person_id
    FROM person p
    WHERE p.removed_on IS NOT NULL
      AND (   p.first_name IS NOT NULL OR p.last_name IS NOT NULL
           OR p.student_number IS NOT NULL OR p.birth_date IS NOT NULL
           OR p.deceased_reported_on IS NOT NULL OR p.deceased_source IS NOT NULL
           OR EXISTS (SELECT 1 FROM contact c          WHERE c.person_id  = p.person_id)
           OR EXISTS (SELECT 1 FROM consent cs         WHERE cs.person_id = p.person_id)
           OR EXISTS (SELECT 1 FROM registration r     WHERE r.person_id  = p.person_id)
           OR EXISTS (SELECT 1 FROM person_expertise e WHERE e.person_id  = p.person_id)
           OR EXISTS (SELECT 1 FROM request rq         WHERE rq.person_id = p.person_id)
           OR EXISTS (SELECT 1 FROM degree d WHERE d.person_id = p.person_id
                      AND (d.name_at_graduation IS NOT NULL
                           OR d.source NOT IN ('registrar', 'spreadsheet'))))"""


def degrees_by_faculty(cur):
    """Q1 by faculty: {faculty: number of degrees}."""
    rows = fetch_all(cur, """SELECT f.name, COUNT(*) FROM degree d
                             JOIN faculty f ON f.faculty_id = d.faculty_id GROUP BY f.name""")
    return dict(rows)
