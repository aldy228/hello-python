-- procedures.sql
-- PostgreSQL stored procedures for the PhoneBook application.
-- Procedures perform actions (INSERT, UPDATE) but do not return data directly.
-- They are called with CALL in Python, unlike functions which use SELECT.
-- Loaded by running option 1 or option 2 from the menu.


-- ─────────────────────────────────────────────
-- add_phone(p_contact_name, p_phone, p_type)
-- Adds a new phone number to an existing contact.
-- Looks up the contact by first name (case-insensitive).
-- Raises an error if the contact is not found.
-- If the same phone number already exists for that contact, updates its type instead.
-- Called in Python as: CALL public.add_phone(%s, %s, %s)
-- ─────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE public.add_phone(
    p_contact_name VARCHAR,  -- first name of the contact to find
    p_phone        VARCHAR,  -- phone number to add
    p_type         VARCHAR   -- type: 'home', 'work', or 'mobile'
)
LANGUAGE plpgsql  -- PL/pgSQL allows IF statements, variables, RAISE, etc.
AS $$
DECLARE
    v_contact_id INTEGER;  -- will hold the found contact's ID
BEGIN
    -- Look up the contact by first name (ILIKE = case-insensitive)
    -- LIMIT 1 in case multiple contacts share the same first name
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;

    -- If no contact was found, raise an error and stop
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    -- Insert the phone; if it already exists for this contact, update its type
    INSERT INTO phones(contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type)
    ON CONFLICT (contact_id, phone)
    DO UPDATE SET type = EXCLUDED.type;
END;
$$;


-- ─────────────────────────────────────────────
-- move_to_group(p_contact_name, p_group_name)
-- Moves a contact to a different group.
-- Creates the group automatically if it doesn't exist yet.
-- Raises an error if the contact is not found.
-- Called in Python as: CALL public.move_to_group(%s, %s)
-- ─────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE public.move_to_group(
    p_contact_name VARCHAR,  -- first name of the contact to move
    p_group_name   VARCHAR   -- name of the target group
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;  -- will hold the found contact's ID
    v_group_id   INTEGER;  -- will hold the target group's ID
BEGIN
    -- Look up the contact by first name
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name ILIKE p_contact_name
    LIMIT 1;

    -- Raise an error if the contact doesn't exist
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    -- Create the group if it doesn't already exist
    -- ON CONFLICT DO NOTHING means no error if the group already exists
    INSERT INTO groups(name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- Fetch the group ID (whether it was just created or already existed)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- Update the contact's group_id to point to the new group
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;