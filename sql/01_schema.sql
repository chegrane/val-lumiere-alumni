-- val-lumiere-alumni — 01_schema.sql
-- Tables, keys, constraints and indexes. See docs/model.md (part 1 and part 3).
-- Run on an empty database: scripts/reset_db.sh rebuilds everything from zero.
--
-- Conventions
--   * On the column's line: primary key, foreign key, NOT NULL, simple UNIQUE, DEFAULT.
--   * Inside CREATE TABLE, after the columns, always named (CONSTRAINT <table>_<rule>):
--     CHECK rules and constraints on several columns.
--     To change one later: DROP CONSTRAINT <name>, then ADD CONSTRAINT <name>, in one transaction.
--   * Outside, after the table: uniqueness on an expression (CREATE UNIQUE INDEX ... (lower(...))).
--   * Names in English, singular, lowercase with underscores.
--   * NULL trap: a CHECK passes when its test is NULL. In rules across columns, prefer
--     IS NULL / IS NOT NULL, which are never NULL (example: request_reason_matches_outcome).
--   * "Not equal" is written <>, the SQL standard form (many languages write it !=; PostgreSQL accepts both).

-- =====================================================================
-- Helper: values that must never change
-- =====================================================================

-- Some values must never change once written (a contact's kind and value, a program's field).
-- A CHECK cannot see the OLD value of a row, so a TRIGGER does it. One generic function, reused:
-- each trigger passes its own message, and fires only WHEN the protected value really changes.
CREATE FUNCTION forbid_update() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION '%', TG_ARGV[0];  -- TG_ARGV[0]: the message given by the trigger
END;
$$;

-- =====================================================================
-- Reference lists
-- =====================================================================

-- One faculty of the university.
CREATE TABLE faculty (
    faculty_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key: created by PostgreSQL
    name        text    NOT NULL,                                  -- e.g. "Engineering"

    -- Not empty, and already cleaned: no spaces at either end.
    -- Without it, ' Engineering ' would get past the unique index below as a second faculty.
    -- (<> means "not equal": it is the SQL standard way to write != .)
    CONSTRAINT faculty_name_trimmed CHECK (name <> '' AND name = btrim(name))
);
-- Unique whatever the case: "Science" and "science" are the same faculty.
CREATE UNIQUE INDEX faculty_name_lower_key ON faculty (lower(name));

-- One field of knowledge, shared by programs and expertise.
CREATE TABLE field (
    field_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    name      text    NOT NULL,                                -- e.g. "Civil engineering"

    -- Not empty, no spaces at either end (same reason as faculty).
    CONSTRAINT field_name_trimmed CHECK (name <> '' AND name = btrim(name))
);
-- Unique whatever the case.
CREATE UNIQUE INDEX field_name_lower_key ON field (lower(name));

-- One study program, at one level, in one faculty (today).
CREATE TABLE program (
    program_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    name        text    NOT NULL,                                  -- e.g. "Bachelor of Civil Engineering"
    level       text    NOT NULL,                                  -- bachelor, master, doctorate, certificate
    faculty_id  integer NOT NULL REFERENCES faculty,  -- foreign key: the faculty that offers it TODAY
                                                      -- (the faculty at graduation is on degree, D-025)
    field_id    integer NOT NULL REFERENCES field,    -- foreign key: its field
                                                      -- (assumption: a program's field does not change)

    -- Not empty, no spaces at either end (same reason as faculty).
    CONSTRAINT program_name_trimmed CHECK (name <> '' AND name = btrim(name)),
    -- A fixed list of allowed levels.
    CONSTRAINT program_level_allowed CHECK (level IN ('bachelor', 'master', 'doctorate', 'certificate'))
);
-- Unique whatever the case.
CREATE UNIQUE INDEX program_name_lower_key ON program (lower(name));
-- A program's field never changes: past degrees read their field through their program.
-- (IS DISTINCT FROM is "<>" that also works when a value is NULL.)
CREATE TRIGGER program_field_never_changes
    BEFORE UPDATE OF field_id ON program
    FOR EACH ROW WHEN (OLD.field_id IS DISTINCT FROM NEW.field_id)
    EXECUTE FUNCTION forbid_update('program.field_id never changes: past degrees would change field');

-- =====================================================================
-- People and degrees
-- =====================================================================

-- One graduate, once, whatever the number of degrees.
CREATE TABLE person (
    person_id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key (D-015)
    student_number        text    UNIQUE,  -- natural key from the registrar: unique when present,
                                           -- may be missing (old spreadsheets); several NULLs are allowed
    first_name            text,            -- current first name (empty only after a removal)
    last_name             text,            -- current family name (empty only after a removal)
    birth_date            date,            -- tells apart two people with the same name (duplicates, slice 4)
    deceased_reported_on  date,            -- the day we learned of the death: filled = no contact at all
    deceased_source       text,            -- how we learned it
    removed_on            date,            -- the day the person's information was removed (model, 1.4)

    -- Texts are already cleaned: not empty, no spaces at either end. NULL passes (a CHECK
    -- only judges values that are present).
    CONSTRAINT person_student_number_trimmed
        CHECK (student_number <> '' AND student_number = btrim(student_number)),
    CONSTRAINT person_first_name_trimmed
        CHECK (first_name <> '' AND first_name = btrim(first_name)),
    CONSTRAINT person_last_name_trimmed
        CHECK (last_name <> '' AND last_name = btrim(last_name)),

    -- A person who was not removed has both names.
    -- "if A then B" is written "NOT A OR B": here, removed OR both names present.
    CONSTRAINT person_names_required_if_active
        CHECK (removed_on IS NOT NULL OR (first_name IS NOT NULL AND last_name IS NOT NULL)),

    -- After a removal, everything that identifies the person is empty.
    CONSTRAINT person_removed_is_empty
        CHECK (removed_on IS NULL
               OR (    first_name           IS NULL
                   AND last_name            IS NULL
                   AND student_number       IS NULL
                   AND birth_date           IS NULL
                   AND deceased_reported_on IS NULL
                   AND deceased_source      IS NULL)),

    -- The death date and its source go together: both filled, or both empty.
    -- (a IS NULL) = (b IS NULL) is true when both are empty or both are filled.
    CONSTRAINT person_deceased_pair
        CHECK ((deceased_reported_on IS NULL) = (deceased_source IS NULL)),

    -- A fixed list of allowed sources.
    CONSTRAINT person_deceased_source_allowed
        CHECK (deceased_source IN ('family', 'returned mail', 'obituary'))
);

-- One degree obtained by one person.
CREATE TABLE degree (
    degree_id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    person_id           integer NOT NULL REFERENCES person,   -- foreign key: who obtained it
    program_id          integer NOT NULL REFERENCES program,  -- foreign key: which program (level, field)
    faculty_id          integer NOT NULL REFERENCES faculty,  -- foreign key: the faculty AT GRADUATION (D-025)
    graduation_year     integer NOT NULL,                     -- the most frequent filter in statistics
    name_at_graduation  text,                                 -- the name printed on the diploma
    source              text    NOT NULL,                     -- 'registrar', or the old spreadsheet's name

    -- The same person cannot have the same program in the same year twice.
    -- (This also creates an index starting with person_id: it speeds up "the degrees of a person".)
    CONSTRAINT degree_once UNIQUE (person_id, program_id, graduation_year),

    -- A plausible year: a sanity check against typing errors (1899, 20012…).
    -- Lower bound: in the story, the oldest records are the faculty spreadsheets of the 1990s.
    CONSTRAINT degree_graduation_year_range
        CHECK (graduation_year BETWEEN 1990 AND 2100),

    -- Texts are already cleaned.
    CONSTRAINT degree_name_at_graduation_trimmed
        CHECK (name_at_graduation <> '' AND name_at_graduation = btrim(name_at_graduation)),
    CONSTRAINT degree_source_trimmed
        CHECK (source <> '' AND source = btrim(source))
);

-- Two rules of the model that a CHECK here CANNOT enforce, because a CHECK sees only its own row:
--   * "After a removal, source is only 'registrar' or 'spreadsheet'": it depends on person.removed_on,
--     a column of another table. Enforced by the removal procedure, verified by the Q9 check query.
--   * "Every person has at least one degree": a foreign key goes from degree to person, never the
--     other way. Enforced by the import process, verified by a test.
--
-- Deleting a person who still has degrees is refused (foreign keys default to NO ACTION).
-- That is what we want: a removal empties the person, it never deletes the row (model, 1.4).
--
-- PostgreSQL does NOT index foreign keys automatically. degree_once covers person_id;
-- indexes on program_id or faculty_id are added only if a measurement shows they are needed.


-- =====================================================================
-- Contacts
-- =====================================================================

-- One email, phone or address of one person.
CREATE TABLE contact (
    contact_id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    person_id          integer NOT NULL REFERENCES person,   -- foreign key: whose contact it is
    kind               text    NOT NULL,                     -- email, phone, address
    label              text    NOT NULL,                     -- university, personal, work
    value              text    NOT NULL,                     -- the address or number itself
    is_preferred       boolean NOT NULL DEFAULT false,       -- the one to use first, for its kind
    status             text    NOT NULL DEFAULT 'unknown',   -- valid, bounced, unknown, obsolete
    status_changed_on  date,                                 -- when the status last changed
    last_checked_on    date,                                 -- last time it was confirmed or delivered
    source             text    NOT NULL,                     -- an imported file's name, "phone call"…

    CONSTRAINT contact_kind_allowed   CHECK (kind   IN ('email', 'phone', 'address')),
    CONSTRAINT contact_label_allowed  CHECK (label  IN ('university', 'personal', 'work')),
    CONSTRAINT contact_status_allowed CHECK (status IN ('valid', 'bounced', 'unknown', 'obsolete')),

    -- Texts are already cleaned: not empty, no spaces at either end.
    CONSTRAINT contact_value_trimmed  CHECK (value  <> '' AND value  = btrim(value)),
    CONSTRAINT contact_source_trimmed CHECK (source <> '' AND source = btrim(source)),

    -- A bounced or obsolete address cannot stay preferred.
    -- "if preferred then usable", written "NOT preferred OR usable".
    CONSTRAINT contact_preferred_is_usable
        CHECK (NOT is_preferred OR status IN ('valid', 'unknown')),

    -- Needed by the two-column link from consent (contact_id, person_id): a consent may only
    -- choose a contact of the same person. A foreign key must point to a UNIQUE set of columns.
    CONSTRAINT contact_id_person_key UNIQUE (contact_id, person_id)
);
-- The same value is not stored twice for the same person and kind, whatever the case:
-- "Lea@Example.org" and "lea@example.org" are the same email.
CREATE UNIQUE INDEX contact_value_lower_key ON contact (person_id, kind, lower(value));
-- At most one preferred contact per person and per kind.
-- A PARTIAL unique index: uniqueness is checked only among the rows WHERE is_preferred.
CREATE UNIQUE INDEX contact_one_preferred ON contact (person_id, kind) WHERE is_preferred;
-- A contact's kind and value never change: a changed address is a NEW row, and the old one
-- becomes 'obsolete'. So its checks, its bounces and the consents that chose it stay attached
-- to the right address. If an old address comes back, its obsolete row is reactivated
-- (the unique index above would refuse a second row with the same value).
CREATE TRIGGER contact_kind_value_never_change
    BEFORE UPDATE OF kind, value ON contact
    FOR EACH ROW WHEN (OLD.kind IS DISTINCT FROM NEW.kind OR OLD.value IS DISTINCT FROM NEW.value)
    EXECUTE FUNCTION forbid_update('contact.kind and contact.value never change: add a new contact instead');

-- =====================================================================
-- Consent
-- =====================================================================

-- The kinds of contact a person can accept or refuse.
CREATE TABLE contact_purpose (
    purpose_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    name        text    NOT NULL,                                  -- e.g. newsletter, events, assignment offers

    CONSTRAINT contact_purpose_name_trimmed CHECK (name <> '' AND name = btrim(name))
);
CREATE UNIQUE INDEX contact_purpose_name_lower_key ON contact_purpose (lower(name));

-- One imported consent list, for one kind of contact (D-028).
CREATE TABLE source_list (
    source_list_id       integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    name                 text        NOT NULL,                           -- e.g. "Newsletter sign-ups 2019"
    purpose_id           integer     NOT NULL REFERENCES contact_purpose, -- foreign key: its ONE kind of contact
    received_at          timestamptz NOT NULL,          -- when the office received it: a "no" blocks from then
    represents_on        date,                          -- the date its information represents, if known
    documented           boolean     NOT NULL DEFAULT false,  -- does it prove consent for its kind?
    evidence_ref         text,                          -- where the proof is
    evidence_checked_on  date,                          -- when the proof was checked
    evidence_checked_by  text,                          -- who checked it

    CONSTRAINT source_list_name_trimmed CHECK (name <> '' AND name = btrim(name)),
    CONSTRAINT source_list_evidence_ref_trimmed
        CHECK (evidence_ref <> '' AND evidence_ref = btrim(evidence_ref)),
    CONSTRAINT source_list_evidence_checked_by_trimmed
        CHECK (evidence_checked_by <> '' AND evidence_checked_by = btrim(evidence_checked_by)),

    -- A documented list has its proof reference, check date and checker; an undocumented one has none.
    CONSTRAINT source_list_evidence_complete
        CHECK (   (    documented
                   AND evidence_ref        IS NOT NULL
                   AND evidence_checked_on IS NOT NULL
                   AND evidence_checked_by IS NOT NULL)
               OR (NOT documented
                   AND evidence_ref        IS NULL
                   AND evidence_checked_on IS NULL
                   AND evidence_checked_by IS NULL)),

    -- Needed by the two-column link from consent (source_list_id, purpose_id).
    CONSTRAINT source_list_id_purpose_key UNIQUE (source_list_id, purpose_id)
);

-- One request made by a person.
CREATE TABLE request (
    request_id   integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    person_id    integer REFERENCES person,  -- foreign key: who asked. Empty only after the person's
                                             -- removal: the kept requests are detached (model, 1.4)
    type         text    NOT NULL,           -- stop, remove, access, correction
    received_on  date    NOT NULL,           -- the legal deadline starts here (access, correction)
    channel      text    NOT NULL,           -- email, phone, letter
    handled_on   date,                       -- empty = still open
    outcome      text,                       -- done, partly done, refused
    reason_code  text,                       -- why, when partly done or refused
    handled_by   text,                       -- which staff member decided

    CONSTRAINT request_type_allowed    CHECK (type    IN ('stop', 'remove', 'access', 'correction')),
    CONSTRAINT request_channel_allowed CHECK (channel IN ('email', 'phone', 'letter')),
    CONSTRAINT request_outcome_allowed CHECK (outcome IN ('done', 'partly done', 'refused')),
    CONSTRAINT request_reason_allowed
        CHECK (reason_code IN ('kept by law', 'identity not verified', 'not held by the office', 'other')),

    -- An access or correction request is in writing.
    CONSTRAINT request_access_in_writing
        CHECK (type NOT IN ('access', 'correction') OR channel IN ('email', 'letter')),

    -- A handled request is complete: date, outcome and who decided, all three or none.
    CONSTRAINT request_handled_complete
        CHECK (    (handled_on IS NULL) = (outcome    IS NULL)
               AND (handled_on IS NULL) = (handled_by IS NULL)),

    -- A reason exists if and only if the request ended NOT fully done (partly done, refused).
    -- NULL TRAP: a CHECK accepts a row when its test is TRUE *or NULL*. Example, an open request
    -- (outcome NULL) with reason 'other':
    --     reason_code IS NULL OR outcome IN ('partly done', 'refused')
    --  =  FALSE               OR NULL                                    =  NULL  ->  accepted!
    -- IS NULL / IS NOT NULL are never NULL, so the version below is always TRUE or FALSE.
    CONSTRAINT request_reason_matches_outcome
        CHECK ((reason_code IS NOT NULL) = (outcome IS NOT NULL AND outcome <> 'done')),

    -- A request is not handled before it was received.
    CONSTRAINT request_handled_after_received
        CHECK (handled_on >= received_on),

    CONSTRAINT request_handled_by_trimmed
        CHECK (handled_by <> '' AND handled_by = btrim(handled_by)),

    -- Needed by the two-column link from consent (request_id, person_id).
    CONSTRAINT request_id_person_key UNIQUE (request_id, person_id)
);
-- Q8 and the removal look up the requests of one person.
CREATE INDEX request_person_idx ON request (person_id);

-- One answer of one person, for one kind of contact (history: rows are only added).
CREATE TABLE consent (
    consent_id      integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    person_id       integer     NOT NULL REFERENCES person,           -- foreign key: who answered
    purpose_id      integer     NOT NULL REFERENCES contact_purpose,  -- foreign key: for what
    granted         boolean     NOT NULL,                             -- yes or no
    given_on        date,                  -- the day the person made the choice (never for a list)
    channel         text        NOT NULL,  -- HOW THE PERSON ANSWERED: email, phone, letter, unsubscribe link, unknown
    entry           text        NOT NULL,  -- HOW IT ENTERED OUR DATABASE: staff, mailing system, file import
    source_list_id  integer,               -- for a file import: its list (two-column foreign key below)
    recorded_at     timestamptz NOT NULL DEFAULT now(),  -- when we recorded it
    recorded_by     text        NOT NULL,  -- which staff member, or which import
    contact_id      integer,               -- where to send this kind (two-column foreign key below)
    request_id      integer,               -- the request that caused it, if any (two-column foreign key below)

    CONSTRAINT consent_channel_allowed
        CHECK (channel IN ('email', 'phone', 'letter', 'unsubscribe link', 'unknown')),
    CONSTRAINT consent_entry_allowed
        CHECK (entry IN ('staff', 'mailing system', 'file import')),
    CONSTRAINT consent_recorded_by_trimmed
        CHECK (recorded_by <> '' AND recorded_by = btrim(recorded_by)),

    -- An answer points to a list if and only if it comes from a list.
    CONSTRAINT consent_list_iff_import
        CHECK ((entry = 'file import') = (source_list_id IS NOT NULL)),

    -- A list snapshot never carries a choice date; the person's own choices always do (D-026, D-028).
    CONSTRAINT consent_given_on_iff_own_choice
        CHECK ((entry = 'file import') = (given_on IS NULL)),

    -- Two-column foreign key: the list must exist AND be about this answer's kind of contact.
    -- (When source_list_id is empty, the link is simply not checked.)
    CONSTRAINT consent_source_list_fk
        FOREIGN KEY (source_list_id, purpose_id) REFERENCES source_list (source_list_id, purpose_id),

    -- Two-column foreign key: the chosen contact must exist AND belong to the same person.
    -- RESTRICT: a contact chosen by a consent cannot be deleted (except at removal, consents first).
    CONSTRAINT consent_contact_fk
        FOREIGN KEY (contact_id, person_id) REFERENCES contact (contact_id, person_id)
        ON DELETE RESTRICT,

    -- Two-column foreign key: the request must exist AND be the same person's.
    -- (Robert's "stop everything" produces three "no" rows that point to ROBERT's request.)
    CONSTRAINT consent_request_fk
        FOREIGN KEY (request_id, person_id) REFERENCES request (request_id, person_id)
);
-- The view current_consent reads the answers of one person and one kind together: this index is
-- its main path (docs/queries.md).
CREATE INDEX consent_person_purpose_idx ON consent (person_id, purpose_id);

-- "The chosen contact is an email" cannot be a CHECK (it needs contact.kind, another table)
-- nor a foreign key. A TRIGGER does it: a small function PostgreSQL runs before each insert
-- or change of contact_id.
CREATE FUNCTION consent_contact_is_email() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.contact_id IS NOT NULL
       AND (SELECT kind FROM contact WHERE contact_id = NEW.contact_id) <> 'email' THEN
        RAISE EXCEPTION 'consent_contact_is_email: the contact chosen for a consent must be an email';
    END IF;
    RETURN NEW;  -- accept the row
END;
$$;

CREATE TRIGGER consent_contact_is_email
    BEFORE INSERT OR UPDATE OF contact_id ON consent
    FOR EACH ROW EXECUTE FUNCTION consent_contact_is_email();

-- "History is never changed" (only INSERT on consent and request) is enforced by rights: slice 5.

-- =====================================================================
-- Suppression list
-- =====================================================================

-- Student numbers that must never be brought back or contacted again, after a removal (D-019, D-022).
-- Linked to NOTHING, on purpose: nothing joins this number back to a program and a year.
CREATE TABLE do_not_contact (
    do_not_contact_id  integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    student_number     text    NOT NULL UNIQUE,  -- the only thing kept; checked at every import
    reason             text    NOT NULL,         -- deceased, stop, removed (deceased > stop > removed)
    since              date    NOT NULL,         -- the date of the reason kept

    CONSTRAINT do_not_contact_reason_allowed
        CHECK (reason IN ('deceased', 'stop', 'removed')),
    CONSTRAINT do_not_contact_student_number_trimmed
        CHECK (student_number <> '' AND student_number = btrim(student_number))
);

-- =====================================================================
-- Events and expertise
-- =====================================================================

-- One event organised by the office.
CREATE TABLE event (
    event_id     integer     GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    title        text        NOT NULL,  -- e.g. "Annual reunion 2026"
    description  text,                  -- free text for the invitation
    starts_at    timestamptz NOT NULL,  -- when
    place        text,                  -- where; empty until decided
    audience     text,                  -- who is targeted, in words; the list itself is computed

    CONSTRAINT event_title_trimmed CHECK (title <> '' AND title = btrim(title)),
    CONSTRAINT event_place_trimmed CHECK (place <> '' AND place = btrim(place))
);

-- One person registered to one event (association class).
CREATE TABLE registration (
    person_id      integer NOT NULL REFERENCES person,  -- foreign key: who
    event_id       integer NOT NULL REFERENCES event,   -- foreign key: which event
    registered_on  date,     -- empty when only the paper list at the door is known
    attended       boolean,  -- did they come? empty = not known yet

    -- The key is the pair: a person registers only once to the same event.
    CONSTRAINT registration_pk PRIMARY KEY (person_id, event_id)
);
-- The primary key starts with person_id; "who registered for this event?" needs event_id first.
CREATE INDEX registration_event_idx ON registration (event_id);

-- One field in which one person has expertise (association class).
CREATE TABLE person_expertise (
    person_id  integer NOT NULL REFERENCES person,  -- foreign key: who
    field_id   integer NOT NULL REFERENCES field,   -- foreign key: which field

    -- The key is the pair: the same field is not recorded twice for the same person.
    CONSTRAINT person_expertise_pk PRIMARY KEY (person_id, field_id)
);
