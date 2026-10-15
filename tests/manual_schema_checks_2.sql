-- Manual checks of the schema (2026-10-14): each block tries to break one rule and should be REFUSED.
-- Run on a throwaway database, after sql/01_schema.sql:
--   createdb val_lumiere_check
--   psql val_lumiere_check -f sql/01_schema.sql
--   psql val_lumiere_check -f tests/manual_schema_checks_2.sql
--   dropdb val_lumiere_check
-- To be turned into automatic tests (pytest) in step 6.

\set ON_ERROR_STOP 0
INSERT INTO faculty (name) VALUES ('Science');
INSERT INTO field (name) VALUES ('Mathematics'), ('Computer science');
INSERT INTO program (name, level, faculty_id, field_id) VALUES ('Bachelor of Mathematics', 'bachelor', 1, 1);
INSERT INTO person (student_number, first_name, last_name) VALUES ('VL1995010', 'Robert', 'Lavoie'), ('VL2024001', 'Léa', 'Fortin');
INSERT INTO contact_purpose (name) VALUES ('newsletter');
INSERT INTO contact (person_id, kind, label, value, is_preferred, status, source) VALUES (2, 'email', 'personal', 'lea@example.org', true, 'valid', 'x');
INSERT INTO request (person_id, type, received_on, channel) VALUES (1, 'stop', '2024-05-10', 'phone');
\echo '--- A open request with a reason (the bug; expect request_reason_matches_outcome)'
INSERT INTO request (person_id, type, received_on, channel, reason_code) VALUES (1, 'remove', '2026-05-01', 'email', 'other');
\echo '--- B refused without a reason (expect request_reason_matches_outcome)'
INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by) VALUES (1, 'remove', '2026-05-01', 'email', '2026-05-02', 'refused', 'staff A');
\echo '--- C Lea consent pointing to Robert request (expect consent_request_fk)'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, request_id) VALUES (2, 1, false, '2024-05-10', 'phone', 'staff', 'staff A', 1);
\echo '--- D change an email into a phone (expect contact_kind_value_never_change)'
UPDATE contact SET kind = 'phone' WHERE contact_id = 1;
\echo '--- E overwrite an email value (expect contact_kind_value_never_change)'
UPDATE contact SET value = 'lea@new.example' WHERE contact_id = 1;
\echo '--- F change a program field (expect program_field_never_changes)'
UPDATE program SET field_id = 2 WHERE program_id = 1;
\echo '--- G documented list with an empty proof reference (expect source_list_evidence_ref_trimmed)'
INSERT INTO source_list (name, purpose_id, received_at, documented, evidence_ref, evidence_checked_on, evidence_checked_by) VALUES ('Sign-ups 2019', 1, now(), true, '', '2026-01-01', 'staff A');
\echo '--- valid (expect no error): Robert consent on his own request; status change allowed; refused with reason'
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, request_id) VALUES (1, 1, false, '2024-05-10', 'phone', 'staff', 'staff A', 1);
UPDATE contact SET status = 'bounced', is_preferred = false WHERE contact_id = 1;
INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, reason_code, handled_by) VALUES (1, 'remove', '2026-05-01', 'email', '2026-05-02', 'refused', 'kept by law', 'staff A');
\echo '--- end'
