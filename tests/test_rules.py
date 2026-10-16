"""The rules give the right answers.

1. The test data itself (so a silently dropped row cannot go unnoticed).
2. The results expected on the test data (docs/queries.md).
3. The edge cases of docs/queries.md, "Edge cases to test", numbered as there (# 1 to # 19).
4. Death and removal: the rules that protect people.
5. Completeness checks: the access report, every person has a degree.

Each test starts from the clean test data: whatever it adds is rolled back afterwards.
"""

import pytest

from helpers import (REMOVAL_CHECK, add_list, add_list_answer, add_own_answer, contact_id,
                     current_answer, degrees_by_faculty, fetch_all, fetch_one, person_id,
                     recipients)


# =====================================================================
# 1. The test data itself
# =====================================================================

def test_test_data_has_every_row(cur):
    # INSERT ... JOIN drops a row silently when a name is mistyped: count everything.
    counts = {table: fetch_one(cur, f"SELECT COUNT(*) FROM {table}")[0]  # our own table names
              for table in ("person", "degree", "contact", "consent", "request", "source_list",
                            "person_expertise")}
    assert counts == {"person": 6, "degree": 7, "contact": 6, "consent": 12, "request": 1,
                      "source_list": 1, "person_expertise": 1}


# =====================================================================
# 2. The expected results on the test data (docs/queries.md)
# =====================================================================

def test_newsletter_goes_to_lea_only(cur):
    # Karim unsubscribed, Robert said stop, Sophie's email bounced, Nadia and Gérard never agreed.
    assert recipients(cur, "newsletter") == ["Léa"]


def test_reunion_invites_lea_and_karim_once_each(cur):
    # Karim has two degrees but receives one invitation; Sophie agreed but cannot be reached.
    assert recipients(cur, "events") == ["Karim", "Léa"]


def test_offers_reach_nadia_only(cur):
    assert recipients(cur, "assignment offers") == ["Nadia"]


def test_sophie_may_but_cannot(cur):
    # The "may but can't" case: she agreed, but her only email bounced.
    assert current_answer(cur, "Sophie", "newsletter")[0] is True
    assert current_answer(cur, "Sophie", "events")[0] is True
    assert fetch_all(cur, "SELECT 1 FROM sendable_email WHERE person_id = %s",
                     (person_id(cur, "Sophie"),)) == []
    assert "Sophie" not in recipients(cur, "newsletter") + recipients(cur, "events")


def test_q1_people_and_degrees_by_faculty(cur):
    rows = fetch_all(cur, """
        SELECT f.name, d.graduation_year,
               COUNT(DISTINCT d.person_id), COUNT(*),
               GROUPING(f.name, d.graduation_year)
        FROM degree d
        JOIN faculty f ON f.faculty_id = d.faculty_id
        GROUP BY CUBE (f.name, d.graduation_year)""")
    total = [(people, degrees) for _, _, people, degrees, level in rows if level == 3]
    by_faculty = {faculty: people for faculty, _, people, _, level in rows if level == 1}
    assert total == [(6, 7)]  # 6 people, 7 degrees: Karim has two
    assert by_faculty == {"Science": 2, "Engineering": 3, "Administration": 1, "Education": 1}
    # The faculty totals of people add up to 7, not 6: never add them (lesson 2).
    assert sum(by_faculty.values()) == 7


def test_q2_reachability(cur):
    active, potential, valid = fetch_one(cur, """
        SELECT (SELECT COUNT(*) FROM active_person),
               (SELECT COUNT(DISTINCT person_id) FROM sendable_email),
               (SELECT COUNT(DISTINCT person_id) FROM sendable_email WHERE status = 'valid')""")
    assert (active, potential, valid) == (6, 4, 3)


def test_q2_reachability_names_not_only_counts(cur):
    # Counts alone would not notice two people swapping their status: check WHO.
    def names(where):
        rows = fetch_all(cur, f"""SELECT DISTINCT p.first_name FROM sendable_email s
                                  JOIN person p USING (person_id) {where}""")  # our own SQL, no input
        return sorted(name for (name,) in rows)
    assert names("") == ["Karim", "Léa", "Nadia", "Robert"]                # potentially reachable
    assert names("WHERE s.status = 'valid'") == ["Karim", "Léa", "Nadia"]  # with a valid email


def test_obsolete_email_is_not_sendable(cur):
    assert fetch_all(cur, "SELECT 1 FROM sendable_email WHERE email = %s",
                     ("lea.fortin@etu.val-lumiere.example",)) == []


def test_q4_engineering_graduates_who_agreed_to_offers(cur):
    rows = fetch_all(cur, """
        SELECT p.first_name
        FROM recipient r
        JOIN person p USING (person_id)
        JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
        WHERE cp.name = 'assignment offers'
          AND EXISTS (SELECT 1 FROM degree d JOIN faculty f ON f.faculty_id = d.faculty_id
                      WHERE d.person_id = r.person_id AND f.name = 'Engineering')""")
    assert rows == [("Nadia",)]


def test_list_b_mathematics_1995_2000_lists_karim_once(cur):
    rows = fetch_all(cur, """
        SELECT p.first_name
        FROM recipient r
        JOIN person p USING (person_id)
        JOIN contact_purpose cp ON cp.purpose_id = r.purpose_id
        WHERE cp.name = 'events'
          AND EXISTS (SELECT 1 FROM degree d
                      JOIN program pr ON pr.program_id = d.program_id
                      JOIN field f    ON f.field_id    = pr.field_id
                      WHERE d.person_id = r.person_id
                        AND f.name = 'Mathematics'
                        AND d.graduation_year BETWEEN 1995 AND 2000)""")
    assert rows == [("Karim",)]


def test_q6_refusals_expressed_by_the_person(cur):
    rows = fetch_all(cur, """
        SELECT p.first_name, cp.name
        FROM current_consent cc
        JOIN active_person   p  ON p.person_id   = cc.person_id
        JOIN contact_purpose cp ON cp.purpose_id = cc.purpose_id
        WHERE NOT cc.granted AND cc.entry <> 'file import'""")
    assert sorted(rows) == [("Karim", "newsletter"),
                            ("Robert", "assignment offers"),
                            ("Robert", "events"),
                            ("Robert", "newsletter")]


def test_no_row_is_not_no(cur):
    # Gérard was never asked: no row at all, and he is not listed as having refused.
    assert current_answer(cur, "Gérard", "newsletter") is None


def test_list_e_is_empty_on_the_test_data(cur):
    assert fetch_all(cur, "SELECT * FROM consent_to_confirm") == []


# =====================================================================
# 3. Edge cases (docs/queries.md, "Edge cases to test")
# =====================================================================

def test_01_documented_list_yes_loses_to_a_later_stop(cur):
    granted, entry, counts_from = current_answer(cur, "Robert", "newsletter")
    assert (granted, entry, str(counts_from)) == (False, "staff", "2024-05-10")


def test_02_unsubscribe_link_beats_an_earlier_yes(cur):
    granted, entry, counts_from = current_answer(cur, "Karim", "newsletter")
    assert (granted, entry, str(counts_from)) == (False, "mailing system", "2026-03-02")
    assert "Karim" not in recipients(cur, "newsletter")


def test_03_list_yes_never_cancels_a_no(cur):
    add_own_answer(cur, "Sophie", "newsletter", False, "2026-03-02")
    stale = add_list(cur, "Old system export", "newsletter",
                     "2026-03-10 09:00 America/Montreal", documented=True)
    add_list_answer(cur, "Sophie", stale, True)
    assert current_answer(cur, "Sophie", "newsletter")[0] is False


def test_04_list_no_blocks_from_the_day_received_in_montreal(cur):
    # Received at 22:30 in Montréal: already the NEXT day in UTC. The session is set to UTC
    # on purpose: the view must still give the office's day (lesson 14).
    cur.execute("SET LOCAL TIME ZONE 'UTC'")
    blocking = add_list(cur, "Returned mail list", "newsletter", "2026-04-01 22:30 America/Montreal")
    add_list_answer(cur, "Léa", blocking, False)
    granted, entry, counts_from = current_answer(cur, "Léa", "newsletter")
    assert (granted, entry, str(counts_from)) == (False, "file import", "2026-04-01")
    assert "Léa" not in recipients(cur, "newsletter")


def test_05_a_later_own_choice_lifts_a_list_block(cur):
    blocking = add_list(cur, "Returned mail list", "newsletter", "2026-04-01 09:00 America/Montreal")
    add_list_answer(cur, "Léa", blocking, False)
    add_own_answer(cur, "Léa", "newsletter", True, "2026-06-01")
    assert current_answer(cur, "Léa", "newsletter")[0] is True
    assert "Léa" in recipients(cur, "newsletter")


def test_06b_list_e_asks_once_even_with_two_lists(cur):
    lists = [add_list(cur, name, "events", "2026-04-01 09:00 America/Montreal")
             for name in ("Reunion 1995", "Reunion 2000")]
    for list_id in reversed(lists):
        add_list_answer(cur, "Gérard", list_id, True)
    rows = fetch_all(cur, "SELECT person_id, source_lists FROM consent_to_confirm")
    assert rows == [(person_id(cur, "Gérard"), sorted(lists))]  # one row, both lists, in a fixed order


def test_06_undocumented_list_yes_gives_no_usable_answer(cur):
    reunion = add_list(cur, "Reunion 1995", "events", "2026-04-01 09:00 America/Montreal")
    add_list_answer(cur, "Gérard", reunion, True)
    assert current_answer(cur, "Gérard", "events") is None
    to_confirm = fetch_all(cur, """SELECT p.first_name FROM consent_to_confirm c
                                   JOIN person p USING (person_id)""")
    assert to_confirm == [("Gérard",)]  # list E


def test_07_proof_found_later_makes_the_list_count(cur):
    reunion = add_list(cur, "Reunion 1995", "events", "2026-04-01 09:00 America/Montreal")
    add_list_answer(cur, "Gérard", reunion, True)
    consents_before = fetch_all(cur, "SELECT * FROM consent ORDER BY consent_id")
    cur.execute("""UPDATE source_list
                   SET documented = true, evidence_ref = 'Forms found in archive box 3',
                       evidence_checked_on = '2026-10-01', evidence_checked_by = 'privacy officer'
                   WHERE source_list_id = %s""", (reunion,))
    assert current_answer(cur, "Gérard", "events")[0] is True
    assert fetch_all(cur, "SELECT * FROM consent_to_confirm") == []                  # out of list E
    assert fetch_all(cur, "SELECT * FROM consent ORDER BY consent_id") == consents_before  # no answer rewritten


def test_08_documented_list_yes_counts_when_alone(cur):
    signups = add_list(cur, "Sign-ups 2018", "newsletter", "2018-09-01 09:00 America/Montreal",
                       documented=True)
    add_list_answer(cur, "Gérard", signups, True)
    assert current_answer(cur, "Gérard", "newsletter")[0] is True


# Cases 9 and 10 (refused by the database) are in test_schema.py.


def test_11_same_day_yes_and_no_from_the_person_gives_no(cur):
    add_own_answer(cur, "Nadia", "newsletter", True, "2026-05-01")
    add_own_answer(cur, "Nadia", "newsletter", False, "2026-05-01")
    assert current_answer(cur, "Nadia", "newsletter")[0] is False


def test_12_unknown_email_is_potential_but_not_valid(cur):
    # Robert's email came from a phone call and was never checked.
    status = fetch_one(cur, "SELECT status FROM sendable_email WHERE person_id = %s",
                       (person_id(cur, "Robert"),))[0]
    assert status == "unknown"                    # we CAN try it...
    assert "Robert" not in recipients(cur, "events")  # ...but we MAY not: he said stop


@pytest.mark.skip(reason="staging tables come with the imports, in slice 3")
def test_13_unconfirmed_staging_row_enters_no_list():
    pass


@pytest.mark.skip(reason="the registrar import comes in slice 3")
def test_14_new_degree_for_a_listed_number_is_ignored():
    pass


def test_15_removal_of_robert(cur):
    # Robert has a request: consents must be deleted BEFORE his request is detached.
    robert = person_id(cur, "Robert")
    by_faculty_before = degrees_by_faculty(cur)
    cur.execute("SELECT remove_person(%s, %s)", (robert, "2026-10-15"))

    assert fetch_all(cur, REMOVAL_CHECK) == []                    # Q9: nothing left
    assert degrees_by_faculty(cur) == by_faculty_before           # Q1: totals unchanged
    assert fetch_one(cur, """SELECT reason, since::text FROM do_not_contact
                             WHERE student_number = 'VL1995010'""") == ("stop", "2024-05-10")
    assert fetch_one(cur, "SELECT person_id FROM request WHERE type = 'stop'") == (None,)  # kept, detached
    for purpose in ("newsletter", "events", "assignment offers"):
        assert "Robert" not in recipients(cur, purpose)


def test_15b_removal_check_finds_a_bad_removal(cur):
    # The check query must FIND a mistake: a removed person who still has a contact.
    leftover = fetch_one(cur, "INSERT INTO person (removed_on) VALUES ('2026-10-15') RETURNING person_id")[0]
    cur.execute("""INSERT INTO contact (person_id, kind, label, value, source)
                   VALUES (%s, 'email', 'personal', 'left@courriel.example', 'test')""", (leftover,))
    assert fetch_all(cur, REMOVAL_CHECK) == [(leftover,)]


def test_15c_suppression_reason_deceased_wins(cur):
    cur.execute("""UPDATE person SET deceased_reported_on = '2026-06-01', deceased_source = 'family'
                   WHERE first_name = 'Robert'""")
    cur.execute("SELECT remove_person(%s, %s)", (person_id(cur, "Robert"), "2026-10-15"))
    assert fetch_one(cur, """SELECT reason, since::text FROM do_not_contact
                             WHERE student_number = 'VL1995010'""") == ("deceased", "2026-06-01")


def test_15d_removal_only_gives_reason_removed(cur):
    cur.execute("SELECT remove_person(%s, %s)", (person_id(cur, "Nadia"), "2026-10-15"))
    assert fetch_one(cur, """SELECT reason, since::text FROM do_not_contact
                             WHERE student_number = 'VL2003027'""") == ("removed", "2026-10-15")
    assert fetch_all(cur, REMOVAL_CHECK) == []


def test_15f_removal_with_a_registration_and_a_chosen_email(cur):
    # The steps a person without these rows would never exercise: a registration to delete,
    # and a consent pointing to an email (consents must go BEFORE contacts: ON DELETE RESTRICT).
    lea = person_id(cur, "Léa")
    cur.execute("INSERT INTO event (title, starts_at) VALUES ('Annual reunion 2026', '2026-11-07 18:00 America/Montreal')")
    cur.execute("INSERT INTO registration (person_id, event_id) SELECT %s, event_id FROM event", (lea,))
    add_own_answer(cur, "Léa", "newsletter", True, "2026-05-01",
                   contact=contact_id(cur, "lea.fortin@courriel.example"))
    cur.execute("SELECT remove_person(%s, %s)", (lea, "2026-10-15"))
    assert fetch_all(cur, REMOVAL_CHECK) == []
    assert fetch_one(cur, "SELECT COUNT(*) FROM registration")[0] == 0


def test_15g_higher_reason_replaces_a_lower_one_on_the_list(cur):
    # Robert's number is already listed as 'removed' (an import let it back in), then he is
    # removed after his stop: the reason becomes 'stop'.
    cur.execute("INSERT INTO do_not_contact (student_number, reason, since) "
                "VALUES ('VL1995010', 'removed', '2025-01-01')")
    cur.execute("SELECT remove_person(%s, %s)", (person_id(cur, "Robert"), "2026-10-15"))
    assert fetch_one(cur, "SELECT reason, since::text FROM do_not_contact "
                          "WHERE student_number = 'VL1995010'") == ("stop", "2024-05-10")


def test_15h_a_removal_needs_a_date(cur):
    with pytest.raises(Exception, match="a removal date is required"):
        cur.execute("SELECT remove_person(%s, NULL)", (person_id(cur, "Nadia"),))


def test_15e_a_person_cannot_be_removed_twice(cur):
    nadia = person_id(cur, "Nadia")
    cur.execute("SELECT remove_person(%s, %s)", (nadia, "2026-10-15"))
    with pytest.raises(Exception, match="already removed"):
        cur.execute("SELECT remove_person(%s, %s)", (nadia, "2026-10-16"))


# Case 16 (access request by phone, refused) is in test_schema.py.


def test_17_same_day_no_from_person_and_list_shows_the_person(cur):
    same_day = add_list(cur, "List received the day of the stop", "newsletter",
                        "2024-05-10 15:00 America/Montreal")
    add_list_answer(cur, "Robert", same_day, False)
    granted, entry, _ = current_answer(cur, "Robert", "newsletter")
    assert (granted, entry) == (False, "staff")  # Q6 can say: Robert refused


def test_18_chosen_email_bounces_no_fallback(cur):
    personal = contact_id(cur, "lea.fortin@courriel.example")
    university = contact_id(cur, "lea.fortin@etu.val-lumiere.example")
    # Léa chooses her personal email for the newsletter...
    add_own_answer(cur, "Léa", "newsletter", True, "2026-05-01", contact=personal)
    # ...then it bounces, and her university email becomes valid and preferred.
    cur.execute("UPDATE contact SET is_preferred = false, status = 'bounced' WHERE contact_id = %s",
                (personal,))
    cur.execute("UPDATE contact SET is_preferred = true, status = 'valid' WHERE contact_id = %s",
                (university,))
    assert "Léa" not in recipients(cur, "newsletter")  # no fallback against her choice
    assert "Léa" in recipients(cur, "events")          # events: no address chosen, so the preferred one


def test_19_no_preferred_and_none_chosen_not_sent(cur):
    cur.execute("""UPDATE contact SET is_preferred = false, status = 'valid'
                   WHERE person_id = %s""", (person_id(cur, "Léa"),))
    assert "Léa" not in recipients(cur, "newsletter")
    assert "Léa" not in recipients(cur, "events")


# =====================================================================
# 4. Death and removal: the rules that protect people
# =====================================================================

def test_a_reported_death_closes_all_contact(cur):
    # The story's painful mistake: an invitation sent to a graduate who had passed away.
    cur.execute("""UPDATE person SET deceased_reported_on = '2026-06-01', deceased_source = 'family'
                   WHERE first_name = 'Léa'""")
    assert "Léa" not in recipients(cur, "newsletter")
    assert "Léa" not in recipients(cur, "events")
    assert fetch_one(cur, "SELECT COUNT(*) FROM active_person")[0] == 5


def test_a_removed_person_is_never_a_recipient(cur):
    # Even with leftovers that a bad removal would leave (a consent and a valid email).
    ghost = fetch_one(cur, "INSERT INTO person (removed_on) VALUES ('2026-10-15') RETURNING person_id")[0]
    cur.execute("""INSERT INTO contact (person_id, kind, label, value, is_preferred, status, source)
                   VALUES (%s, 'email', 'personal', 'ghost@courriel.example', true, 'valid', 'test')""",
                (ghost,))
    cur.execute("""INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by)
                   SELECT %s, purpose_id, true, '2026-01-01', 'email', 'staff', 'test'
                   FROM contact_purpose WHERE name = 'newsletter'""", (ghost,))
    assert fetch_all(cur, "SELECT 1 FROM recipient WHERE person_id = %s", (ghost,)) == []


# =====================================================================
# 5. Completeness checks
# =====================================================================

# Q8 of docs/queries.md: one query per class that points to a person.
ACCESS_REPORT_TABLES = {"person", "degree", "contact", "consent", "request", "registration",
                        "person_expertise"}


def test_access_report_covers_every_table_with_a_person_id(cur):
    # If a table with a person_id is added later, the access report (Q8) must be updated too.
    rows = fetch_all(cur, """
        SELECT c.table_name
        FROM information_schema.columns c
        JOIN information_schema.tables t
          ON t.table_schema = c.table_schema AND t.table_name = c.table_name
        WHERE c.table_schema = 'public' AND c.column_name = 'person_id'
          AND t.table_type = 'BASE TABLE'""")
    assert {name for (name,) in rows} == ACCESS_REPORT_TABLES


def test_every_person_has_at_least_one_degree(cur):
    # A foreign key cannot enforce it (it goes from degree to person): a check query does.
    assert fetch_all(cur, """SELECT person_id FROM person p
                             WHERE NOT EXISTS (SELECT 1 FROM degree d WHERE d.person_id = p.person_id)""") == []


def test_status_change_records_its_date(cur):
    # Without a date given: the office's today. With a date given (an import): that date.
    lea = "lea.fortin@courriel.example"
    cur.execute("UPDATE contact SET status = 'bounced', is_preferred = false WHERE value = %s", (lea,))
    today = fetch_one(cur, "SELECT (now() AT TIME ZONE 'America/Montreal')::date")[0]
    assert fetch_one(cur, "SELECT status_changed_on FROM contact WHERE value = %s", (lea,))[0] == today
    cur.execute("UPDATE contact SET status = 'valid', status_changed_on = '2026-09-30' WHERE value = %s",
                (lea,))
    assert str(fetch_one(cur, "SELECT status_changed_on FROM contact WHERE value = %s", (lea,))[0]) \
        == "2026-09-30"
