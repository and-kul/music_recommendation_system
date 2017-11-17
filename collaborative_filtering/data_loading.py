import math
import numpy as np
import psycopg2
from scipy.sparse import lil_matrix

from config import Config

select_top_songs_sql = """SELECT song_id FROM top_songs ORDER BY position ASC LIMIT %s;"""
select_top_users_sql = """SELECT user_id FROM top_users ORDER BY position ASC LIMIT %s;"""

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


def remove_users_with_few_songs(dataset: lil_matrix, threshold: int) -> lil_matrix:
    """
    Removes users with songs_count < threshold, returning new lil_matrix

    :param dataset: user-song lil_matrix
    :param threshold: required minimum number of songs for a users
    :return: new version of dataset
    """
    good_users = set(range(dataset.shape[0]))
    for i in range(dataset.shape[0]):
        if dataset[i].count_nonzero() < threshold:
            good_users.remove(i)

    good_users = list(good_users)
    return dataset[good_users]




def get_dataset(users_count: int, songs_count: int, minimum_songs_per_user: int, make_binary=False,
                make_log=False, add_one=False) -> lil_matrix:
    if make_binary and make_log:
        raise Exception("cannot be binary and log at the same time")
    if add_one and not make_log:
        raise Exception("add_one available only with make_log")


    conn = None

    if make_log:
        dataset = lil_matrix((users_count, songs_count), dtype=np.float64)
    else:
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

            if make_log and add_one:
                dataset[user_pos, song_pos] = math.log2(play_count + 1)
            elif make_log:
                dataset[user_pos, song_pos] = math.log2(play_count)
            elif make_binary:
                dataset[user_pos, song_pos] = 1
            else:
                dataset = play_count

        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
        raise
    finally:
        if conn is not None:
            conn.close()

    dataset = remove_users_with_few_songs(dataset, threshold=minimum_songs_per_user)

    return dataset
