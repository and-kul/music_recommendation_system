import sqlite3
import psycopg2
from pprint import pprint
from config import Config

from_echo_nest_to_integer_song_id = {}

error_tracks = set()

with open(r"C:\workspace\IR\sid_mismatches.txt", encoding="utf-8") as mismatches_file:
    for line in mismatches_file.readlines():
        track_id = line[27:45]
        error_tracks.add(track_id)

with sqlite3.connect(r"C:\workspace\IR\track_metadata_old.db") as sqlite_conn, \
     psycopg2.connect(**Config.get_postgresql_conn_parameters()) as postgres_conn:
    select_songs_sql = """SELECT track_id, song_id, title, release, artist_id,
        artist_name, duration, "year" FROM songs;"""

    insert_track_metadata = """INSERT INTO "public".track_metadata(track_id, song_id, title, release,
artist_id, artist_name, duration, "year") VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    insert_song = """INSERT INTO "public".songs(echo_nest_id) VALUES (%s) RETURNING id;"""

    postgres_cur = postgres_conn.cursor()
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute(select_songs_sql)

    row = sqlite_cur.fetchone()

    rows_inserted = 0

    while row is not None:
        track_id = row[0]
        song_echo_nest_id = row[1]
        title = row[2]
        release = row[3]
        artist_id = row[4]
        artist_name = row[5]
        duration = row[6]
        year = row[7] if row[7] != 0 else None
        # print(track_id)
        if track_id in error_tracks:
            row = sqlite_cur.fetchone()
            continue

        song_id = from_echo_nest_to_integer_song_id.get(song_echo_nest_id, None)

        if song_id is None:
            # add new song_echo_nest_id
            postgres_cur.execute(insert_song, (song_echo_nest_id,))
            # get integer song_id from postgres
            song_id = postgres_cur.fetchone()[0]
            from_echo_nest_to_integer_song_id[song_echo_nest_id] = song_id


        # add track metadata
        postgres_cur.execute(insert_track_metadata,
                             (track_id, song_id, title, release, artist_id, artist_name, duration, year))
        rows_inserted += 1
        if rows_inserted % 10000 == 0:
            postgres_conn.commit()
            print("Rows inserted:", rows_inserted)

        row = sqlite_cur.fetchone()

    sqlite_cur.close()
    postgres_conn.commit()
    postgres_cur.close()
