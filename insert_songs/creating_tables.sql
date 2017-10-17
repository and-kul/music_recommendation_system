-- DROP TABLE IF EXISTS track_metadata;
-- DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
  id SERIAL PRIMARY KEY,
  echo_nest_id TEXT NOT NULL UNIQUE
);
-- unique index for echo_nest_id already created

CREATE TABLE track_metadata (
  track_id    TEXT PRIMARY KEY,
  song_id     INTEGER NOT NULL REFERENCES songs (id) ON DELETE CASCADE,
  title       TEXT,
  release     TEXT,
  artist_id   TEXT NOT NULL,
  artist_name TEXT,
  duration    FLOAT8,
  year        INT
);

CREATE INDEX ON track_metadata (song_id);
CREATE INDEX ON track_metadata (artist_id);
CREATE INDEX ON track_metadata (artist_name);
