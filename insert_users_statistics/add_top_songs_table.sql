DROP TABLE IF EXISTS top_songs;


CREATE TABLE top_songs (
  position       SERIAL PRIMARY KEY,
  song_id        INTEGER NOT NULL REFERENCES songs (id) ON DELETE CASCADE,
  users_per_song INTEGER NOT NULL
);


INSERT INTO top_songs (song_id, users_per_song) (SELECT
                                                   tmp.song_id,
                                                   tmp.users_per_song
                                                 FROM (SELECT
                                                         song_id,
                                                         count(*) AS users_per_song
                                                       FROM users_songs
                                                       GROUP BY song_id) AS tmp
                                                 ORDER BY tmp.users_per_song DESC);
