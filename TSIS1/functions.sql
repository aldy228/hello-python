-- functions.sql
-- PostgreSQL functions used by the PhoneBook application.
-- Functions return data (unlike procedures which perform actions).
-- Loaded by running option 1 or option 2 from the menu.


-- ─────────────────────────────────────────────
-- get_contacts_page(p_limit, p_offset)
-- Returns one page of contacts for paginated browsing.
-- p_limit  = how many rows to return (page size)
-- p_offset = how many rows to skip (page number * page size)
-- Example: get_contacts_page(5, 10) returns rows 11-15
-- Called in Python as: SELECT * FROM public.get_contacts_page(%s, %s)
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.get_contacts_page(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    surname    VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE sql  -- simple SQL function, no procedural logic needed
AS $$
    SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id  -- LEFT JOIN keeps contacts with no group
    ORDER BY c.name, c.surname               -- consistent ordering across pages
    LIMIT p_limit OFFSET p_offset;           -- LIMIT = page size, OFFSET = starting position
$$;


-- ─────────────────────────────────────────────
-- search_contacts(p_query)
-- Full-text search across multiple fields.
-- Searches: name, surname, email, and ALL phone numbers.
-- Uses ILIKE for case-insensitive partial matching.
-- Uses DISTINCT to avoid duplicate rows when a contact has multiple matching phones.
-- Called in Python as: SELECT * FROM public.search_contacts(%s)
-- ─────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    surname    VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE sql
AS $$
    SELECT DISTINCT c.id, c.name, c.surname, c.email, c.birthday, g.name
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON p.contact_id = c.id  -- join phones so we can search phone numbers
    WHERE
        c.name    ILIKE '%' || p_query || '%'   -- matches if name contains the query
     OR c.surname ILIKE '%' || p_query || '%'   -- matches if surname contains the query
     OR c.email   ILIKE '%' || p_query || '%'   -- matches if email contains the query
     OR p.phone   ILIKE '%' || p_query || '%'   -- matches if any phone number contains the query
    ORDER BY c.name, c.surname;
$$;