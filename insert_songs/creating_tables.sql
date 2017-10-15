-- DROP TABLE IF EXISTS track_metadata;
-- DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
  id text PRIMARY KEY
);


CREATE TABLE track_metadata (
  track_id    TEXT PRIMARY KEY,
  title       TEXT,
  song_id     TEXT NOT NULL REFERENCES songs (id) ON DELETE CASCADE,
  release     TEXT,
  artist_id   TEXT NOT NULL,
  artist_name TEXT,
  duration    FLOAT8,
  year        INT
);

CREATE INDEX ON track_metadata (song_id);
CREATE INDEX ON track_metadata (artist_id);
CREATE INDEX ON track_metadata (artist_name);
