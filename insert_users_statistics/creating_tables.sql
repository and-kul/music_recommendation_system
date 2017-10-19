DROP TABLE IF EXISTS users_songs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id   SERIAL PRIMARY KEY,
  hash TEXT NOT NULL UNIQUE
);
-- unique index for hash already created

CREATE TABLE users_songs (
  user_id    INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  song_id    INTEGER NOT NULL REFERENCES songs (id) ON DELETE CASCADE,
  play_count INT  NOT NULL,
  PRIMARY KEY (user_id, song_id)
);

CREATE INDEX ON users_songs (song_id);
