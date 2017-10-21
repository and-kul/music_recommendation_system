from pprint import pprint
from typing import List

import numpy as np
from scipy.sparse import lil_matrix
import psycopg2
from config import Config

songs_count = 10000
users_count = 10000

select_top_songs_sql = """SELECT song_id FROM top_songs ORDER BY position ASC LIMIT %s;"""
select_top_users_sql = """SELECT user_id FROM top_users ORDER BY position ASC LIMIT %s;"""

# select_user_songs_sql = """SELECT song_id FROM users_songs WHERE user_id = %s;"""

select_top_users_with_songs_sql = """
SELECT
  user_id,
  song_id,
  play_count
FROM (SELECT *
      FROM top_users
      ORDER BY position ASC
      LIMIT %s) AS tmp
  NATURAL JOIN users_songs;
"""

conn = None
dataset = lil_matrix((users_count, songs_count), dtype=np.int32)

try:
    conn = psycopg2.connect(**Config.get_postgresql_conn_parameters())
    cur = conn.cursor()

    cur.execute(select_top_songs_sql, (songs_count,))
    rows = cur.fetchall()
    from_song_id_to_pos = {row[0]: i for i, row in enumerate(rows)}

    cur.execute(select_top_users_sql, (users_count,))
    rows = cur.fetchall()
    from_user_id_to_pos = {row[0]: i for i, row in enumerate(rows)}


    cur.execute(select_top_users_with_songs_sql, (users_count,))
    rows = cur.fetchall()
    for row in rows:
        user_id = row[0]
        song_id = row[1]
        play_count = row[2]

        user_pos = from_user_id_to_pos[user_id]

        song_pos = from_song_id_to_pos.get(song_id, None)
        # we don't consider a song, if it's not from top songs_count
        if song_pos is None:
            continue

        dataset[user_pos, song_pos] = 1

    print(dataset.count_nonzero() / (dataset.shape[0] * dataset.shape[1]))


    cur.close()
except psycopg2.DatabaseError as error:
    print(error)
    raise
finally:
    if conn is not None:
        conn.close()
