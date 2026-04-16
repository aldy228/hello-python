
CREATE OR REPLACE PROCEDURE upsert_contact(_name text, _secondname text, _phone text)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO phonebook(firstname, secondname, phonenumber)
    VALUES(_name, _secondname, _phone)
    ON CONFLICT(phonenumber) DO UPDATE
    SET firstname = EXCLUDED.firstname,
        secondname = EXCLUDED.secondname;
END;
$$;

CREATE OR REPLACE PROCEDURE bulk_upsert_contacts(_names text[], _secondnames text[], _phones text[])
LANGUAGE plpgsql AS $$
DECLARE
    i integer;
BEGIN
    FOR i IN array_lower(_names,1)..array_upper(_names,1) LOOP
        CALL upsert_contact(_names[i], _secondnames[i], _phones[i]);
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(_value text)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook WHERE firstname = _value OR secondname = _value OR phonenumber = _value;
END;
$$;