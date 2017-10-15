DROP TABLE IF EXISTS users_songs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id TEXT PRIMARY KEY
);

CREATE TABLE users_songs (
  user_id    TEXT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  song_id    TEXT NOT NULL REFERENCES songs (id) ON DELETE CASCADE,
  play_count INT  NOT NULL,
  PRIMARY KEY (user_id, song_id)
);

CREATE INDEX ON users_songs (song_id);
