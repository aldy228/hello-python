-- schema.sql
-- Defines the full database structure for the PhoneBook application.
-- Running this file drops all existing tables and recreates them from scratch.
-- WARNING: all data is lost when this file is executed.

-- Drop tables in reverse dependency order (phones depends on contacts, contacts depends on groups)
-- CASCADE means any foreign key references are also dropped automatically
DROP TABLE IF EXISTS phones CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS groups CASCADE;

-- groups table: stores contact categories like Family, Work, Friend, Other
-- Each group has a unique name so we can safely upsert by name
CREATE TABLE groups (
    id   SERIAL PRIMARY KEY,          -- auto-incrementing unique ID
    name VARCHAR(50) UNIQUE NOT NULL  -- group name must be unique and non-empty
);

-- contacts table: one row per person
-- name + surname together must be unique (used as the natural key for upserts)
CREATE TABLE contacts (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL,
    surname    VARCHAR(50)  NOT NULL,
    email      VARCHAR(100),                         -- optional email address
    birthday   DATE,                                 -- optional birthday (YYYY-MM-DD)
    group_id   INTEGER REFERENCES groups(id),        -- foreign key to groups table (optional)
    date_added TIMESTAMP DEFAULT NOW(),              -- automatically set to current time on insert
    UNIQUE (name, surname)                           -- prevent duplicate contacts
);

-- phones table: stores multiple phone numbers per contact (1-to-many relationship)
-- When a contact is deleted, all their phone numbers are automatically deleted too (CASCADE)
CREATE TABLE phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,   -- link to contact
    phone      VARCHAR(20) NOT NULL,                                 -- the phone number string
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')), -- allowed values only
    UNIQUE (contact_id, phone)   -- a contact can't have the same number twice
);