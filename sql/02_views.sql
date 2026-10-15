-- val-lumiere-alumni — 02_views.sql
-- The four building blocks of docs/queries.md. Each business rule is written ONCE, here;
-- every list (newsletter, invitations, offers…) reads these views.
-- Run after 01_schema.sql.
--
--   active_person    not reported deceased, not removed
--   sendable_email   CAN:  the emails we may try
--   current_consent  MAY:  the person's usable answer today, per kind of contact
--   recipient        CAN AND MAY: who receives what, at which address
--
-- A view stores no data: it is a saved query, recomputed each time it is read.
-- So these views are always up to date (a "stop" counts at once).
-- A MATERIALIZED view would store the result and need a REFRESH: faster to read, but stale between
-- two refreshes. Fine for statistics, never for consent (docs/lessons.md, lessons 19 and 20).

-- =====================================================================
-- active_person — not reported deceased, not removed
-- =====================================================================
-- A person with a reported death, or whose information was removed, is never contacted.
-- Written once, here, it protects every list (the story's painful mistake).
-- (The database cannot KNOW that someone is alive: only that no death was reported.)
--
-- Only the columns the lists need. A view is also an interface: in slice 5, roles will read
-- views, not tables; student_number and birth_date have no reason to be visible here.
CREATE VIEW active_person AS
SELECT person_id,
       first_name,
       last_name
FROM person
WHERE deceased_reported_on IS NULL
  AND removed_on IS NULL;

-- =====================================================================
-- sendable_email — CAN: the emails we may try
-- =====================================================================
-- 'valid'  : a message was delivered, or the person confirmed it.
-- 'unknown': never checked, never shown to fail: worth trying.
-- 'bounced' and 'obsolete' are left out.
-- "sendable" means "we may try", not "it works": Q2 counts 'valid' separately.
CREATE VIEW sendable_email AS
SELECT c.contact_id,
       c.person_id,
       c.value AS email,
       c.status,
       c.is_preferred
FROM contact c
JOIN active_person p ON p.person_id = c.person_id   -- only active people
WHERE c.kind = 'email'
  AND c.status IN ('valid', 'unknown');

-- =====================================================================
-- current_consent — MAY: the usable answer today, per person and kind of contact
-- =====================================================================
-- Three kinds of evidence (D-026, D-028):
--   1. the person's own choice, with its real date   -> counts from that date
--   2. a "no" from an imported list                  -> counts from the day the office RECEIVED the list
--   3. a "yes" from an imported list                 -> only if nothing else exists,
--                                                       and only if the list proves consent
-- Then: the latest wins; on the same day, "no" wins; same day and same answer: the person's
-- own choice is shown rather than a list (Q6 then says "Robert refused", not "a list blocks").
--
-- NO ROW IS NOT "NO": a person with no row has no usable answer (never asked, or only a "yes"
-- from a list that proves nothing). Either way, nothing is sent. List E finds the second case.
CREATE VIEW current_consent AS
SELECT DISTINCT ON (person_id, purpose_id)       -- keep ONE row per person and kind: the first one
       person_id,                                -- in the ORDER BY below
       purpose_id,
       granted,
       counts_from,
       channel,
       entry,
       source_list_id,
       contact_id
FROM (
    SELECT c.*,
           CASE
             -- Asked FIRST: does the answer come from a list? (A list never uses a choice date.)
             WHEN c.entry = 'file import' AND NOT c.granted
                  THEN (sl.received_at AT TIME ZONE 'America/Montreal')::date
                                                -- 2. a list's "no": the OFFICE's calendar day of receipt
             WHEN c.entry = 'file import'
                  THEN '-infinity'::date        -- 3. a list's "yes": older than any date, wins only alone
             ELSE c.given_on                    -- 1. the person's own choice: its real date
           END AS counts_from
    FROM consent c
    LEFT JOIN source_list sl ON sl.source_list_id = c.source_list_id   -- empty for the person's own choices
    WHERE NOT (c.entry = 'file import'
               AND c.granted
               AND NOT sl.documented)           -- a "yes" from a list that proves nothing is set aside
) AS c
ORDER BY person_id, purpose_id,
         counts_from DESC,     -- the latest first
         granted,              -- same day: "no" (false sorts before true) first
         (entry = 'file import'),  -- same day, same answer: the person's own choice (false) first
         recorded_at DESC,     -- still tied: the last one recorded
         consent_id DESC;      -- final tie-breaker, so the result never changes from one run to the next

-- =====================================================================
-- recipient — CAN AND MAY: who receives what, at which address
-- =====================================================================
-- A person appears only if they pass BOTH tests:
--   MAY: their current answer for this kind of contact is "yes"   (WHERE cc.granted)
--   CAN: a sendable email matches                                  (the JOIN)
-- Which email? The one chosen for this kind if any; otherwise the preferred email.
-- If the chosen email is no longer sendable, the JOIN finds nothing: not sent, on purpose
-- (Léa said "only my personal email"). No preferred and none chosen: not sent either.
CREATE VIEW recipient AS
SELECT cc.person_id,
       cc.purpose_id,
       se.contact_id,     -- which contact row was used (for an invitation history, later)
       se.email
FROM current_consent cc
JOIN sendable_email se
  ON se.person_id = cc.person_id
 AND (   se.contact_id = cc.contact_id                    -- the email chosen for this kind
      OR (cc.contact_id IS NULL AND se.is_preferred))     -- otherwise the preferred email
WHERE cc.granted;
