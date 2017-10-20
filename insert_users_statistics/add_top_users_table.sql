DROP TABLE IF EXISTS top_users;


CREATE TABLE top_users (
  position       SERIAL PRIMARY KEY,
  user_id        INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  songs_per_user INTEGER NOT NULL
);


INSERT INTO top_users (user_id, songs_per_user) (SELECT
                                                   tmp.user_id,
                                                   tmp.songs_per_user
                                                 FROM (SELECT
                                                         user_id,
                                                         count(*) AS songs_per_user
                                                       FROM users_songs
                                                       GROUP BY user_id) AS tmp
                                                 ORDER BY tmp.songs_per_user DESC);
