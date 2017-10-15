import psycopg2

from config import Config

select_song_sql = "SELECT * FROM songs WHERE id = %s LIMIT 1;"
select_user_sql = "SELECT * FROM users WHERE id = %s LIMIT 1;"

insert_user_sql = "INSERT INTO users (id) VALUES (%s);"
insert_triplet_sql = """INSERT INTO users_songs (user_id, song_id, play_count) VALUES (%s, %s, %s);"""

with open(r"C:\workspace\IR\train_triplets.txt") as triplets_file, \
     psycopg2.connect(**Config.get_postgresql_conn_parameters()) as conn:
    cur = conn.cursor()
    line = triplets_file.readline()
    triplets_count = 0
    while line:
        triplets_count += 1

        words = line.split()
        user_id = words[0]
        song_id = words[1]
        play_count = int(words[2])

        cur.execute(select_song_sql, (song_id,))
        song_result = cur.fetchone()
        if song_result is None:
            line = triplets_file.readline()
            continue

        cur.execute(select_user_sql, (user_id, ))
        user_result = cur.fetchone()
        if user_result is None:
            cur.execute(insert_user_sql, (user_id, ))

        cur.execute(insert_triplet_sql, (user_id, song_id, play_count))

        # print("user_id={}, song_id={}, play_count={}".format(user_id, song_id, play_count))

        if triplets_count % 100000 == 0:
            conn.commit()
            print(triplets_count)
        line = triplets_file.readline()

    cur.close()
