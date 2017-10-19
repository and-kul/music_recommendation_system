import psycopg2

from config import Config

select_all_songs_sql = "SELECT echo_nest_id, id FROM songs;"
insert_user_sql = "INSERT INTO users (hash) VALUES (%s) RETURNING id;"
insert_triplet_sql = """INSERT INTO users_songs (user_id, song_id, play_count) VALUES (%s, %s, %s);"""

from_hash_to_user_id = {}


with open(r"C:\workspace\IR\train_triplets.txt") as triplets_file, \
     psycopg2.connect(**Config.get_postgresql_conn_parameters()) as conn, \
     conn.cursor() as cur:

    # load mapping from postgres
    cur.execute(select_all_songs_sql)
    from_echo_nest_to_integer_song_id = dict(cur.fetchall())

    line = triplets_file.readline()
    triplets_count = 0
    while line:
        words = line.split()
        user_hash = words[0]
        song_echo_nest_id = words[1]
        play_count = int(words[2])

        song_id = from_echo_nest_to_integer_song_id.get(song_echo_nest_id, None)

        # no such song in database
        if song_id is None:
            line = triplets_file.readline()
            continue

        user_id = from_hash_to_user_id.get(user_hash, None)

        if user_id is None:
            # add new user hash
            cur.execute(insert_user_sql, (user_hash,))
            # get integer user_id from postgres
            user_id = cur.fetchone()[0]
            from_hash_to_user_id[user_hash] = user_id

        cur.execute(insert_triplet_sql, (user_id, song_id, play_count))
        triplets_count += 1

        if triplets_count % 100000 == 0:
            conn.commit()
            print(triplets_count)

        line = triplets_file.readline()
        pass

    conn.commit()
