DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS raw_announcements;
DROP TABLE IF EXISTS timed_announcements;
DROP TABLE IF EXISTS timed_announcement_backups;
DROP TABLE IF EXISTS timed_raw_announcements;
DROP TABLE IF EXISTS timed_raw_announcement_backups;

CREATE TABLE IF NOT EXISTS settings(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    guild_id BIGINT NOT NULL UNIQUE,
    allowed_roles BIGINT[] NOT NULL,
    prefix TEXT NOT NULL DEFAULT 'a!'
);

CREATE TABLE IF NOT EXISTS timed_announcements(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    expires TIMESTAMPTZ NOT NULL,
    channel_id BIGINT NOT NULL,
    embed_details JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS announcements(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    channel_id BIGINT NOT NULL,
    embed_details JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_announcements(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    channel_id BIGINT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timed_raw_announcements(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    expires TIMESTAMPTZ NOT NULL,
    channel_id BIGINT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timed_raw_announcement_backups(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    expires TIMESTAMPTZ NOT NULL,
    channel_id BIGINT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS timed_announcement_backups(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    announcement_id INTEGER NOT NULL UNIQUE,
    expires TIMESTAMPTZ NOT NULL,
    channel_id BIGINT NOT NULL,
    embed_details JSONB NOT NULL
);