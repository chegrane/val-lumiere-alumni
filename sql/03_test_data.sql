-- val-lumiere-alumni — 03_test_data.sql
-- Small, hand-made test data: the reference lists and the six people of docs/queries.md
-- (Léa, Robert, Sophie, Karim, Nadia, Gérard). Every expected result is known in advance:
-- docs/queries.md gives, for each question, what this data must return.
-- All names, numbers and addresses are invented. Emails use the reserved domain ".example".
-- Run after 01_schema.sql and 02_views.sql.
--
-- Identifiers are never typed by hand (lesson 12: they can have gaps). Each row finds the
-- rows it points to by a meaningful value: a name, a student number.
--
-- ┌──────────────────────────────────────────────────────────────────────────────────────┐
-- │ MANUAL DATA, written by hand, for tests only.                                         │
-- │ Real data will NOT be entered like this: from slice 3 on, it comes from CSV files,    │
-- │ read by a Python program and sent to PostgreSQL with PARAMETERIZED queries (values    │
-- │ travel separately from the SQL text: the protection against SQL injection), through   │
-- │ staging tables where it is cleaned before entering these tables.                     │
-- └──────────────────────────────────────────────────────────────────────────────────────┘
--
-- THE DATA AT A GLANCE (a reading aid; the SQL below is the source of truth).
--
-- person: student_number, first_name, last_name, birth_date
--   VL2024015, Léa,    Fortin,    2001-04-12
--   VL1995010, Robert, Lavoie,    1971-09-03
--   VL2009033, Sophie, Roy,       1986-02-20
--   VL1998042, Karim,  Haddad,    1976-07-15
--   VL2003027, Nadia,  Belkacem,  1980-11-30
--   (none),    Gérard, Pelletier, (none)          <- from an old spreadsheet
--
-- degree: person, program, faculty at graduation, year, name on the diploma, source
--   Léa,    Bachelor of Computer Science,        Science,        2024, Léa Fortin,       registrar
--   Robert, Bachelor of Business Administration, Administration, 1995, Robert Lavoie,    registrar
--   Sophie, Bachelor of Education,               Education,      2009, Sophie Gagnon,    registrar  <- former name
--   Karim,  Bachelor of Mathematics,             Science,        1998, Karim Haddad,     registrar
--   Karim,  Master of Civil Engineering,         Engineering,    2012, Karim Haddad,     registrar  <- second degree
--   Nadia,  Bachelor of Civil Engineering,       Engineering,    2003, Nadia Belkacem,   registrar
--   Gérard, Bachelor of Civil Engineering,       Engineering,    1995, Gérard Pelletier, genie_1995.xlsx
--
-- contact (all emails): person, label, value, preferred, status
--   Léa,    personal,   lea.fortin@courriel.example,          yes, valid
--   Léa,    university, lea.fortin@etu.val-lumiere.example,   no,  obsolete
--   Robert, personal,   robert.lavoie@courriel.example,       yes, valid
--   Sophie, personal,   sophie.roy@courriel.example,          no,  bounced
--   Karim,  personal,   karim.haddad@courriel.example,        yes, unknown
--   Nadia,  work,       nadia.belkacem@genie-conseil.example, yes, valid
--   (Gérard: no contact)
--
-- consent history: person, kind, answer, date, how the person answered, how it entered
--   Robert, newsletter,        yes, (list),     unknown,          file import "Newsletter sign-ups 2019" (documented)
--   Robert, newsletter,        no,  2024-05-10, phone,            staff  (his "stop" request)
--   Robert, events,            no,  2024-05-10, phone,            staff  (same request)
--   Robert, assignment offers, no,  2024-05-10, phone,            staff  (same request)
--   Léa,    newsletter,        yes, 2025-01-10, email,            staff
--   Léa,    events,            yes, 2025-01-10, email,            staff
--   Sophie, newsletter,        yes, 2020-03-01, email,            staff
--   Sophie, events,            yes, 2020-03-01, email,            staff
--   Karim,  newsletter,        yes, 2026-01-15, email,            staff
--   Karim,  events,            yes, 2026-01-15, email,            staff
--   Karim,  newsletter,        no,  2026-03-02, unsubscribe link, mailing system
--   Nadia,  assignment offers, yes, 2025-09-01, email,            staff
--   (Gérard: never asked)
--
-- expertise: Nadia, Civil engineering

BEGIN;  -- all or nothing: if one insert fails, none of them stays

-- =====================================================================
-- Reference lists
-- =====================================================================

INSERT INTO faculty (name) VALUES
    ('Science'), ('Engineering'), ('Administration'), ('Education');

INSERT INTO field (name) VALUES
    ('Computer science'), ('Mathematics'), ('Civil engineering'), ('Management'), ('Education');

-- program: name, level, faculty (today), field
INSERT INTO program (name, level, faculty_id, field_id)
SELECT p.name, p.level, f.faculty_id, fd.field_id
FROM (VALUES
    ('Bachelor of Computer Science',        'bachelor', 'Science',        'Computer science'),
    ('Bachelor of Mathematics',             'bachelor', 'Science',        'Mathematics'),
    ('Bachelor of Civil Engineering',       'bachelor', 'Engineering',    'Civil engineering'),
    ('Master of Civil Engineering',         'master',   'Engineering',    'Civil engineering'),
    ('Bachelor of Business Administration', 'bachelor', 'Administration', 'Management'),
    ('Bachelor of Education',               'bachelor', 'Education',      'Education')
) AS p(name, level, faculty, field)
JOIN faculty f  ON f.name  = p.faculty     -- find each id by its name
JOIN field   fd ON fd.name = p.field;

INSERT INTO contact_purpose (name) VALUES
    ('newsletter'), ('events'), ('assignment offers');

-- =====================================================================
-- The six people
-- =====================================================================

INSERT INTO person (student_number, first_name, last_name, birth_date) VALUES
    ('VL2024015', 'Léa',    'Fortin',    '2001-04-12'),
    ('VL1995010', 'Robert', 'Lavoie',    '1971-09-03'),
    ('VL2009033', 'Sophie', 'Roy',       '1986-02-20'),
    ('VL1998042', 'Karim',  'Haddad',    '1976-07-15'),
    ('VL2003027', 'Nadia',  'Belkacem',  '1980-11-30');
-- Gérard comes from an old faculty spreadsheet: no student number, no birth date.
INSERT INTO person (first_name, last_name) VALUES ('Gérard', 'Pelletier');

-- Degrees: who (student number, or last name for Gérard), program, faculty AT GRADUATION, year,
-- name printed on the diploma, source.
INSERT INTO degree (person_id, program_id, faculty_id, graduation_year, name_at_graduation, source)
SELECT pe.person_id, pr.program_id, f.faculty_id, d.year, d.name_on_diploma, d.source
FROM (VALUES
    ('VL2024015', NULL,        'Bachelor of Computer Science',        'Science',        2024, 'Léa Fortin',       'registrar'),
    ('VL1995010', NULL,        'Bachelor of Business Administration', 'Administration', 1995, 'Robert Lavoie',    'registrar'),
    ('VL2009033', NULL,        'Bachelor of Education',               'Education',      2009, 'Sophie Gagnon',    'registrar'),  -- her former name
    ('VL1998042', NULL,        'Bachelor of Mathematics',             'Science',        1998, 'Karim Haddad',     'registrar'),
    ('VL1998042', NULL,        'Master of Civil Engineering',         'Engineering',    2012, 'Karim Haddad',     'registrar'),
    ('VL2003027', NULL,        'Bachelor of Civil Engineering',       'Engineering',    2003, 'Nadia Belkacem',   'registrar'),
    (NULL,        'Pelletier', 'Bachelor of Civil Engineering',       'Engineering',    1995, 'Gérard Pelletier', 'genie_1995.xlsx')
) AS d(student_number, last_name, program, faculty, year, name_on_diploma, source)
JOIN person  pe ON pe.student_number = d.student_number
                OR (d.student_number IS NULL AND pe.last_name = d.last_name)
JOIN program pr ON pr.name = d.program
JOIN faculty f  ON f.name  = d.faculty;

-- Nadia declared civil engineering as her expertise.
INSERT INTO person_expertise (person_id, field_id)
SELECT pe.person_id, f.field_id
FROM person pe, field f
WHERE pe.student_number = 'VL2003027' AND f.name = 'Civil engineering';

-- =====================================================================
-- Contacts
-- =====================================================================
-- Léa: personal email valid (preferred), university email obsolete (she stopped reading it).
-- Robert: valid. Sophie: her only email bounced (so it cannot be preferred).
-- Karim: never checked ('unknown'). Nadia: work email valid. Gérard: none.
INSERT INTO contact (person_id, kind, label, value, is_preferred, status, last_checked_on, source)
SELECT pe.person_id, 'email', c.label, c.value, c.preferred, c.status, c.checked, c.source
FROM (VALUES
    ('VL2024015', 'personal',   'lea.fortin@courriel.example',             true,  'valid',    DATE '2025-01-10', 'email from the person'),
    ('VL2024015', 'university', 'lea.fortin@etu.val-lumiere.example',      false, 'obsolete', NULL,              'registrar'),
    ('VL1995010', 'personal',   'robert.lavoie@courriel.example',          true,  'valid',    DATE '2024-04-02', 'phone call'),
    ('VL2009033', 'personal',   'sophie.roy@courriel.example',             false, 'bounced',  NULL,              'email from the person'),
    ('VL1998042', 'personal',   'karim.haddad@courriel.example',           true,  'unknown',  NULL,              'phone call'),
    ('VL2003027', 'work',       'nadia.belkacem@genie-conseil.example',    true,  'valid',    DATE '2025-09-01', 'email from the person')
) AS c(student_number, label, value, preferred, status, checked, source)
JOIN person pe ON pe.student_number = c.student_number;

-- =====================================================================
-- Consent
-- =====================================================================

-- Robert is in a documented 2019 newsletter sign-up list (the sign-up forms prove it).
INSERT INTO source_list (name, purpose_id, received_at, represents_on, documented,
                         evidence_ref, evidence_checked_on, evidence_checked_by)
SELECT 'Newsletter sign-ups 2019', purpose_id, '2019-06-01 09:00 America/Montreal', '2019-05-31', true,
       'Sign-up forms 2019, archive box 12', '2019-06-03', 'privacy officer'
FROM contact_purpose WHERE name = 'newsletter';

INSERT INTO consent (person_id, purpose_id, granted, channel, entry, source_list_id, recorded_by)
SELECT pe.person_id, sl.purpose_id, true, 'unknown', 'file import', sl.source_list_id, 'import 2019'
FROM person pe, source_list sl
WHERE pe.student_number = 'VL1995010' AND sl.name = 'Newsletter sign-ups 2019';

-- Robert's "stop everything", by phone, on 2024-05-10: one request, three "no" answers.
INSERT INTO request (person_id, type, received_on, channel, handled_on, outcome, handled_by)
SELECT person_id, 'stop', '2024-05-10', 'phone', '2024-05-10', 'done', 'newsletter manager'
FROM person WHERE student_number = 'VL1995010';

INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by, request_id)
SELECT pe.person_id, cp.purpose_id, false, '2024-05-10', 'phone', 'staff', 'newsletter manager', r.request_id
FROM person pe
JOIN request r ON r.person_id = pe.person_id AND r.type = 'stop'
CROSS JOIN contact_purpose cp            -- one row per kind of contact: newsletter, events, offers
WHERE pe.student_number = 'VL1995010';

-- The person's own choices, typed by the staff or sent by the mailing system.
INSERT INTO consent (person_id, purpose_id, granted, given_on, channel, entry, recorded_by)
SELECT pe.person_id, cp.purpose_id, a.granted, a.given_on, a.channel, a.entry, a.recorded_by
FROM (VALUES
    ('VL2024015', 'newsletter',        true,  DATE '2025-01-10', 'email',            'staff',          'newsletter manager'),
    ('VL2024015', 'events',            true,  DATE '2025-01-10', 'email',            'staff',          'events coordinator'),
    ('VL2009033', 'newsletter',        true,  DATE '2020-03-01', 'email',            'staff',          'newsletter manager'),
    ('VL2009033', 'events',            true,  DATE '2020-03-01', 'email',            'staff',          'events coordinator'),
    ('VL1998042', 'newsletter',        true,  DATE '2026-01-15', 'email',            'staff',          'newsletter manager'),
    ('VL1998042', 'events',            true,  DATE '2026-01-15', 'email',            'staff',          'events coordinator'),
    ('VL1998042', 'newsletter',        false, DATE '2026-03-02', 'unsubscribe link', 'mailing system', 'Office 365 import'),
    ('VL2003027', 'assignment offers', true,  DATE '2025-09-01', 'email',            'staff',          'faculty secretary')
) AS a(student_number, purpose, granted, given_on, channel, entry, recorded_by)
JOIN person          pe ON pe.student_number = a.student_number
JOIN contact_purpose cp ON cp.name           = a.purpose;

COMMIT;
