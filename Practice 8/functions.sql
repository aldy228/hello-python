CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p text)
RETURNS TABLE(firstname VARCHAR, secondname VARCHAR, phonenumber VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT c.firstname, c.secondname, c.phonenumber FROM phonebook c
                 WHERE c.firstname ILIKE '%' || p || '%'
                    OR c.secondname ILIKE '%' || p || '%'
                    OR c.phonenumber ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(_limit integer, _offset integer)
RETURNS TABLE(firstname varchar, secondname varchar, phonenumber varchar)
AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM phonebook
    LIMIT _limit OFFSET _offset;
END;
$$ LANGUAGE plpgsql;