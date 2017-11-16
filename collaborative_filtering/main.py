from pprint import pprint
from typing import List

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
import psycopg2
from sklearn.model_selection import train_test_split
import random
import time
from pandas import DataFrame

from config import Config
from item_based_filtering import ItemBasedFiltering


random.seed("music")

# alpha = 0.5
# q = 1
test_proportion = 0.2
minimum_songs_per_user = 2
songs_count = 20
users_count = 20
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


start_time = time.time()

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

        # no exact play count information
        dataset[user_pos, song_pos] = 1

    cur.close()
except psycopg2.DatabaseError as error:
    print(error)
    raise
finally:
    if conn is not None:
        conn.close()

dataset = remove_users_with_few_songs(dataset, threshold=minimum_songs_per_user)

# print(dataset.count_nonzero() / (dataset.shape[0] * dataset.shape[1]))

# print(dataset.toarray())





X_train, X_test = train_test_split(dataset, test_size=test_proportion, random_state=0)
# todo: remove these annotations
X_train: csr_matrix
X_test: csr_matrix

X_test = X_test.tolil()

train_size = X_train.shape[0]
test_size = X_test.shape[0]
print("train_size =", train_size)
print("test_size =", test_size)

# pprint(X_test.toarray())

secret_songs = [None] * test_size


for i in range(test_size):
    listened_songs = X_test[i].nonzero()[1].tolist()
    secret_songs[i] = random.sample(listened_songs, len(listened_songs)//2)
    X_test[i, secret_songs[i]] = 0

# pprint(secret_songs)
# pprint(X_test.toarray())

X_test = X_test.tocsr()

# print(X_train.toarray())
# print(X_test.toarray())


print("--- %s seconds ---" % (time.time() - start_time))

item_based_filtering = ItemBasedFiltering(X_train, X_test, secret_songs)

from_q_and_alpha_to_MAP = DataFrame(None, index=[1, 2, 3, 4, 5],
                                    columns=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], dtype=np.float64)

for q in [1, 2, 3, 4, 5]:
    for alpha in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        MAP = item_based_filtering.calculate_MAP(alpha=alpha, q=q)
        print("alpha = {0}, q = {1}, MAP = {2:.6f}".format(alpha, q, MAP))
        from_q_and_alpha_to_MAP.loc[q, alpha] = MAP
        print("--- %s seconds ---" % (time.time() - start_time))

    print()

from_q_and_alpha_to_MAP.to_csv("results.csv", float_format="%.4f")


