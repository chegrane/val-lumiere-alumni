"""The database refuses what it must refuse, and accepts what it must accept.

Each REFUSED case: a few setup statements (may be empty), then ONE statement that must
fail, and the name of the rule that must refuse it: the constraint's name, or for a
trigger, the start of its message. Checking the name matters: a row refused by the
WRONG rule would hide a missing one.

These replace the manual checks tried by hand on 2026-10-14.
"""

import psycopg
import pytest

LEA_DEGREE = """SELECT d.person_id, d.program_id, d.faculty_id, d.graduation_year
                FROM degree d JOIN person p USING (person_id) WHERE p.first_name = 'Léa'"""

REFUSED = [
    # --- reference lists ---
    ("faculty_name_lower_key", [],
     "INSERT INTO faculty (name) VALUES ('science')"),
    ("faculty_name_trimmed", [],
     "INSERT INTO faculty (name) VALUES (' Law ')"),

    # --- person and degree ---
    ("degree_once", [],
     f"INSERT INTO degree (person_id, program_id, faculty_id, graduation_year, source) "
     f"SELECT person_id, program_id, faculty_id, graduation_year, 'registrar' FROM ({LEA_DEGREE}) AS d"),
    ("degree_graduation_year_range", [],
     "UPDATE degree SET graduation_year = 20012 "
     "WHERE person_id = (SELECT person_id FROM person WHERE first_name = 'Léa')"),
    ("person_names_required_if_active", [],
     "INSERT INTO person (first_name) VALUES ('Paul')"),
    ("person_deceased_pair", [],
     "UPDATE person SET deceased_reported_on = '2026-01-01' WHERE first_name = 'Robert'"),
    ("person_removed_is_empty", [],
     "UPDATE person SET removed_on = '2026-01-01' WHERE first_name = 'Robert'"),
    ("person_deceased_pair", [],  # the other half: a source without a date
     "UPDATE person SET deceased_source = 'family' WHERE first_name = 'Robert'"),
    ("person_removed_is_empty", [],  # removed, but the death information is still there
     "INSERT INTO person (removed_on, deceased_reported_on, deceased_source) "
     "VALUES ('2026-01-01', '2025-12-01', 'family')"),
    ("person_student_number_format", [],  # lowercase would get past UNIQUE and the suppression list
     "INSERT INTO person (student_number, first_name, last_name) VALUES ('vl2030001', 'Paul', 'Côté')"),
    ("do_not_contact_student_number_format", [],
     "INSERT INTO do_not_contact (student_number, reason, since) VALUES ('vl2003027', 'removed', '2026-01-01')"),
    ("degree_person_id_fkey", [],  # a removal empties a person, it never deletes the row
     "DELETE FROM person WHERE first_name = 'Gérard'"),

    # --- contacts ---
    ("contact_one_preferred", [],
     "INSERT INTO contact (person_id, kind, label, value, is_preferred, source) "
     "SELECT person_id, 'email', 'work', 'karim@work.example', true, 'test' "
     "FROM person WHERE first_name = 'Karim'"),
    ("contact_value_lower_key", [],
     "INSERT INTO contact (person_id, kind, label, value, source) "
     "SELECT person_id, 'email', 'work', 'KARIM.HADDAD@courriel.example', 'test' "
     "FROM person WHERE first_name = 'Karim'"),
    ("contact_preferred_is_usable", [],
     "UPDATE contact SET status = 'bounced' WHERE value = 'lea.fortin@courriel.example'"),
    ("contact_preferred_is_usable", [],
     "UPDATE contact SET status = 'obsolete' WHERE value = 'lea.fortin@courriel.example'"),
    ("contact.kind and contact.value never change", [],
     "UPDATE contact SET kind = 'phone' WHERE value = 'lea.fortin@courriel.example'"),
    ("contact.kind and contact.value never change", [],
     "UPDATE contact SET value = 'lea@new.example' WHERE value = 'lea.fortin@courriel.example'"),
    ("program.field_id never changes", [],
     "UPDATE program SET field_id = (SELECT field_id FROM field WHERE name = 'Mathematics') "
     "WHERE name = 'Bachelor of Computer Science'"),

    # --- consent ---
    ("consent_contact_fk", [],  # Karim's consent pointing to Léa's email
     "INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, contact_id) "
     "SELECT p.person_id, cp.purpose_id, true, '2026-05-01', 'email', 'staff', 'test', c.contact_id "
     "FROM person p, contact_purpose cp, contact c "
     "WHERE p.first_name = 'Karim' AND cp.name = 'events' AND c.value = 'lea.fortin@courriel.example'"),
    ("consent_contact_is_email",  # a consent pointing to a phone
     ["INSERT INTO contact (person_id, kind, label, value, source) "
      "SELECT person_id, 'phone', 'personal', '819-555-0101', 'test' FROM person WHERE first_name = 'Karim'"],
     "INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, contact_id) "
     "SELECT p.person_id, cp.purpose_id, true, '2026-05-01', 'phone', 'staff', 'test', c.contact_id "
     "FROM person p, contact_purpose cp, contact c "
     "WHERE p.first_name = 'Karim' AND cp.name = 'events' AND c.value = '819-555-0101'"),
    ("consent_source_list_fk",  # edge case 9: a documented newsletter list used for assignment offers
     [],
     "INSERT INTO consent (person_id, purpose_id, granted, channel, entry, source_list_id, recorded_by) "
     "SELECT p.person_id, cp.purpose_id, true, 'unknown', 'file import', sl.source_list_id, 'test' "
     "FROM person p, contact_purpose cp, source_list sl "
     "WHERE p.first_name = 'Gérard' AND cp.name = 'assignment offers' "
     "AND sl.name = 'Newsletter sign-ups 2019'"),
    ("consent_list_iff_import", [],  # a file import that names no list
     "INSERT INTO consent (person_id, purpose_id, granted, channel, entry, recorded_by) "
     "SELECT p.person_id, cp.purpose_id, true, 'unknown', 'file import', 'test' "
     "FROM person p, contact_purpose cp WHERE p.first_name = 'Gérard' AND cp.name = 'events'"),
    ("consent_given_on_iff_own_choice", [],  # the person's own choice without its date
     "INSERT INTO consent (person_id, purpose_id, granted, channel, entry, recorded_by) "
     "SELECT p.person_id, cp.purpose_id, true, 'email', 'staff', 'test' "
     "FROM person p, contact_purpose cp WHERE p.first_name = 'Gérard' AND cp.name = 'events'"),
    ("consent_given_on_not_after_recording", [],  # "2062" typed instead of "2026"
     "INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by) "
     "SELECT p.person_id, cp.purpose_id, true, '2062-05-10', 'email', 'staff', 'test' "
     "FROM person p, contact_purpose cp WHERE p.first_name = 'Karim' AND cp.name = 'newsletter'"),
    ("consent_given_on_iff_own_choice",  # edge case 10: a list answer with a choice date
     ["INSERT INTO source_list (name, purpose_id, received_at) "
      "SELECT 'Reunion 1995', purpose_id, now() FROM contact_purpose WHERE name = 'events'"],
     "INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, source_list_id, recorded_by) "
     "SELECT p.person_id, sl.purpose_id, true, '1995-05-01', 'unknown', 'file import', sl.source_list_id, 'test' "
     "FROM person p, source_list sl WHERE p.first_name = 'Gérard' AND sl.name = 'Reunion 1995'"),
    ("consent_request_fk", [],  # Léa's consent pointing to Robert's request
     "INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, request_id) "
     "SELECT p.person_id, cp.purpose_id, false, '2024-05-10', 'phone', 'staff', 'test', r.request_id "
     "FROM person p, contact_purpose cp, request r "
     "WHERE p.first_name = 'Léa' AND cp.name = 'events' AND r.type = 'stop'"),

    # --- source lists ---
    ("source_list_evidence_complete", [],
     "INSERT INTO source_list (name, purpose_id, received_at, documented) "
     "SELECT 'Sign-ups 2020', purpose_id, now(), true FROM contact_purpose WHERE name = 'newsletter'"),
    ("source_list_evidence_complete", [],  # the other half: an undocumented list carrying proof
     "INSERT INTO source_list (name, purpose_id, received_at, evidence_ref) "
     "SELECT 'Sign-ups 2020', purpose_id, now(), 'box 4' FROM contact_purpose WHERE name = 'newsletter'"),
    ("source_list_represents_before_received", [],
     "INSERT INTO source_list (name, purpose_id, received_at, represents_on) "
     "SELECT 'Sign-ups 2020', purpose_id, '2020-01-10 09:00 America/Montreal', '2020-02-01' "
     "FROM contact_purpose WHERE name = 'newsletter'"),
    ("source_list_evidence_ref_trimmed", [],
     "INSERT INTO source_list (name, purpose_id, received_at, documented, evidence_ref, "
     "evidence_checked_on, evidence_checked_by) "
     "SELECT 'Sign-ups 2020', purpose_id, now(), true, '', '2026-01-01', 'test' "
     "FROM contact_purpose WHERE name = 'newsletter'"),

    # --- requests ---
    ("request_access_in_writing", [],  # edge case 16
     "INSERT INTO request (person_id, type, received_on, channel) "
     "SELECT person_id, 'access', '2026-05-01', 'phone' FROM person WHERE first_name = 'Robert'"),
    ("request_handled_after_received", [],
     "INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by) "
     "SELECT person_id, 'stop', '2026-05-02', 'phone', '2026-05-01', 'done', 'test' "
     "FROM person WHERE first_name = 'Robert'"),
    ("request_handled_complete", [],
     "INSERT INTO request (person_id, type, received_on, channel, handled_on) "
     "SELECT person_id, 'stop', '2026-05-01', 'phone', '2026-05-01' FROM person WHERE first_name = 'Robert'"),
    ("request_reason_matches_outcome", [],  # THE NULL TRAP: an open request with a reason
     "INSERT INTO request (person_id, type, received_on, channel, reason_code) "
     "SELECT person_id, 'remove', '2026-05-01', 'email', 'other' FROM person WHERE first_name = 'Robert'"),
    ("request_reason_matches_outcome", [],  # refused, but no reason
     "INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by) "
     "SELECT person_id, 'remove', '2026-05-01', 'email', '2026-05-02', 'refused', 'test' "
     "FROM person WHERE first_name = 'Robert'"),

    # --- events ---
    ("registration_pk",
     ["INSERT INTO event (title, starts_at) VALUES ('Annual reunion 2026', '2026-11-07 18:00 America/Montreal')",
      "INSERT INTO registration (person_id, event_id) "
      "SELECT p.person_id, e.event_id FROM person p, event e WHERE p.first_name = 'Léa'"],
     "INSERT INTO registration (person_id, event_id) "
     "SELECT p.person_id, e.event_id FROM person p, event e WHERE p.first_name = 'Léa'"),
]


@pytest.mark.parametrize("rule, setup, statement", REFUSED,
                         ids=[f"{i:02d}-{case[0][:40]}" for i, case in enumerate(REFUSED, 1)])
def test_refused(cur, rule, setup, statement):
    for sql in setup:
        cur.execute(sql)
    with pytest.raises(psycopg.Error) as error:
        cur.execute(statement)
    refused_by = error.value.diag.constraint_name or error.value.diag.message_primary or ""
    assert rule == refused_by or refused_by.startswith(rule), f"refused by {refused_by!r}, not {rule!r}"


ACCEPTED = [
    # A contact's STATUS may change (only its kind and value never do).
    ("status change", "UPDATE contact SET status = 'bounced', is_preferred = false "
                      "WHERE value = 'lea.fortin@courriel.example'"),
    # A fully done request needs no reason.
    ("done without reason",
     "INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by) "
     "SELECT person_id, 'stop', '2026-05-01', 'phone', '2026-05-01', 'done', 'test' "
     "FROM person WHERE first_name = 'Robert'"),
    # A refused request with its reason.
    ("refused with reason",
     "INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, reason_code, handled_by) "
     "SELECT person_id, 'remove', '2026-05-01', 'email', '2026-05-02', 'refused', 'kept by law', 'test' "
     "FROM person WHERE first_name = 'Robert'"),
    # A removed person with everything empty.
    ("removed and empty", "INSERT INTO person (removed_on) VALUES ('2026-01-01')"),
    # A second person without a student number: several NULLs are allowed by UNIQUE.
    ("second missing student number", "INSERT INTO person (first_name, last_name) VALUES ('Paul', 'Côté')"),
]


@pytest.mark.parametrize("name, statement", ACCEPTED, ids=[case[0] for case in ACCEPTED])
def test_accepted(cur, name, statement):
    cur.execute(statement)  # must not raise


def test_choice_dated_the_montreal_day_is_accepted_from_any_session_time_zone(cur):
    # Recorded at 00:30 in Montréal on Oct 16: still Oct 15 in Vancouver. The CHECK must use
    # the office's day, not the session's, or this correct row would be refused.
    cur.execute("SET LOCAL TIME ZONE 'America/Vancouver'")
    cur.execute("""INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry,
                                        recorded_by, recorded_at)
                   SELECT p.person_id, cp.purpose_id, true, '2026-10-16', 'email', 'staff', 'test',
                          '2026-10-16 00:30 America/Montreal'
                   FROM person p, contact_purpose cp
                   WHERE p.first_name = 'Gérard' AND cp.name = 'events'""")


def test_list_describing_its_montreal_day_of_receipt_is_accepted_from_any_session_time_zone(cur):
    cur.execute("SET LOCAL TIME ZONE 'America/Vancouver'")
    cur.execute("""INSERT INTO source_list (name, purpose_id, received_at, represents_on)
                   SELECT 'Sign-ups Feb 2020', purpose_id, '2020-02-01 00:30 America/Montreal', '2020-02-01'
                   FROM contact_purpose WHERE name = 'newsletter'""")
