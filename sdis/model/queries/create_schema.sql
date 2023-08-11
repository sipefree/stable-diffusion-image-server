-- -- -- ALBUM -- -- --

CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(name) > 0),
    original_path TEXT NOT NULL,
    generated_path TEXT NOT NULL,
    parent_id INTEGER REFERENCES Album(id) ON DELETE CASCADE,
    thumbnail_path TEXT NOT NULL,
    creation_timestamp TEXT NOT NULL
);

-- Indexes

-- This index will speed up lookups by parent_id, useful for queries where we want to find all child albums of a given parent.
CREATE INDEX idx_album_parent_id ON albums(parent_id);

-- Additional indexes can be created based on query patterns. For example:
-- If you frequently query by `name`, then:
-- CREATE INDEX idx_album_name ON Album(name);


-- -- -- Image -- -- --

CREATE TABLE albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL REFERENCES Album(id) ON DELETE CASCADE,
    original_path TEXT NOT NULL,
    fullsize_thumbnail_path TEXT NOT NULL,
    large_thumbnail_path TEXT NOT NULL,
    small_thumbnail_path TEXT NOT NULL,
    width INTEGER NOT NULL CHECK(width > 0),
    height INTEGER NOT NULL CHECK(height > 0),
    creation_timestamp TEXT NOT NULL,
    origfile_size INTEGER NOT NULL CHECK(origfile_size > 0),
    origfile_hash TEXT NOT NULL,
    parameters_text TEXT NOT NULL,
    parameters JSON NOT NULL
);

-- Indexes

-- This index will speed up lookups by album_id, useful for queries where we want to find all images in a given album.
CREATE INDEX idx_image_album_id ON Image(album_id);

-- If you frequently query or join on the origfile_hash:
CREATE INDEX idx_image_origfile_hash ON Image(origfile_hash);

-- Creating the FTS5 table for Image parameters_text
CREATE VIRTUAL TABLE images_fts USING fts5(id UNINDEXED, parameters_text, content='images');
