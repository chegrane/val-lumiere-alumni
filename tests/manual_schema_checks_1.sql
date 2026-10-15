-- Manual checks of the schema (2026-10-14): each block tries to break one rule and should be REFUSED.
-- Run on a throwaway database, after sql/01_schema.sql:
--   createdb val_lumiere_check
--   psql val_lumiere_check -f sql/01_schema.sql
--   psql val_lumiere_check -f tests/manual_schema_checks_1.sql
--   dropdb val_lumiere_check
-- To be turned into automatic tests (pytest) in step 6.

\set ON_ERROR_STOP 0
INSERT INTO faculty (name) VALUES ('Science');
INSERT INTO field (name) VALUES ('Mathematics');
INSERT INTO program (name, level, faculty_id, field_id) VALUES ('Bachelor of Mathematics', 'bachelor', 1, 1);
INSERT INTO person (student_number, first_name, last_name) VALUES ('VL1998042', 'Karim', 'Haddad');
INSERT INTO person (student_number, first_name, last_name) VALUES ('VL2024001', 'Léa', 'Fortin');
INSERT INTO contact_purpose (name) VALUES ('newsletter'), ('events');
INSERT INTO contact (person_id, kind, label, value, is_preferred, status, source)
  VALUES (1, 'email', 'personal', 'karim@example.org', true, 'unknown', 'phone call'),
         (1, 'phone', 'personal', '819-555-0101', true, 'valid', 'phone call'),
         (2, 'email', 'personal', 'lea@example.org', true, 'valid', 'email from the person');
INSERT INTO source_list (name, purpose_id, received_at) VALUES ('Reunion 1995', 2, '2026-04-01 09:00');
\echo '--- 1 second preferred email for Karim (expect contact_one_preferred)'
INSERT INTO contact (person_id, kind, label, value, is_preferred, source) VALUES (1, 'email', 'work', 'k@work.example', true, 'x');
\echo '--- 2 same email, other case (expect contact_value_lower_key)'
INSERT INTO contact (person_id, kind, label, value, source) VALUES (1, 'email', 'work', 'KARIM@example.org', 'x');
\echo '--- 3 bounced but preferred (expect contact_preferred_is_usable)'
INSERT INTO contact (person_id, kind, label, value, is_preferred, status, source) VALUES (2, 'phone', 'work', '1', true, 'bounced', 'x');
\echo '--- 4 Karim consent pointing to Lea email (expect consent_contact_fk)'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, contact_id) VALUES (1, 1, true, '2026-01-15', 'email', 'staff', 'staff A', 3);
\echo '--- 5 consent pointing to a phone (expect trigger consent_contact_is_email)'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, contact_id) VALUES (1, 1, true, '2026-01-15', 'email', 'staff', 'staff A', 2);
\echo '--- 6 events list used for the newsletter (expect consent_source_list_fk)'
INSERT INTO consent (person_id, purpose_id, granted, channel, entry, source_list_id, recorded_by) VALUES (1, 1, true, 'unknown', 'file import', 1, 'import 1');
\echo '--- 7 list answer with a choice date (expect consent_given_on_iff_own_choice)'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, source_list_id, recorded_by) VALUES (1, 2, true, '1995-05-01', 'unknown', 'file import', 1, 'import 1');
\echo '--- 8 access request by phone (expect request_access_in_writing)'
INSERT INTO request (person_id, type, received_on, channel) VALUES (1, 'access', '2026-05-01', 'phone');
\echo '--- 9 handled without outcome (expect request_handled_complete)'
INSERT INTO request (person_id, type, received_on, channel, handled_on) VALUES (1, 'stop', '2026-05-01', 'phone', '2026-05-01');
\echo '--- 10 documented list without proof (expect source_list_evidence_complete)'
INSERT INTO source_list (name, purpose_id, received_at, documented) VALUES ('Sign-ups 2019', 1, now(), true);
\echo '--- 11 Lea registered twice to the same event (expect registration_pk)'
INSERT INTO event (title, starts_at) VALUES ('Annual reunion 2026', '2026-11-07 18:00-05');
INSERT INTO registration (person_id, event_id) VALUES (2, 1);
INSERT INTO registration (person_id, event_id) VALUES (2, 1);
\echo '--- valid rows (expect no error)'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, contact_id) VALUES (1, 1, true, '2026-01-15', 'email', 'staff', 'staff A', 1);
INSERT INTO consent (person_id, purpose_id, granted, channel, entry, source_list_id, recorded_by) VALUES (1, 2, true, 'unknown', 'file import', 1, 'import 1');
INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by) VALUES (1, 'stop', '2026-05-01', 'phone', '2026-05-01', 'done', 'staff A');
INSERT INTO do_not_contact (student_number, reason, since) VALUES ('VL1990007', 'removed', '2025-11-03');
\echo '--- end'
