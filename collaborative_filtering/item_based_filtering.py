import numpy as np
from scipy.sparse import csr_matrix
from typing import List


class ItemBasedFiltering:
    def __init__(self, X_train: csr_matrix, X_test: csr_matrix, secret_songs: List[List[int]], data_is_binary: bool):
        self.data_is_binary = data_is_binary
        self.X_train = X_train
        self.X_test = X_test
        self.secret_songs = secret_songs
        self.train_size = X_train.shape[0]
        self.test_size = X_test.shape[0]
        self.songs_count = X_train.shape[1]

    def calculate_songs_similarity(self, alpha, q) -> np.ndarray:
        songs_similarity = np.zeros((self.songs_count, self.songs_count))
        array = self.X_train.toarray()





        if self.data_is_binary:
            users_count_for_song = [0] * self.songs_count
            for song_i in range(self.songs_count):
                users_count_for_song[song_i] = np.count_nonzero(array[:, song_i])

            for song_i in range(self.songs_count):
                song_i_users_count = users_count_for_song[song_i]
                for song_j in range(self.songs_count):
                    song_j_users_count = users_count_for_song[song_j]
                    intersection_size = np.count_nonzero(array[:, song_i] * array[:, song_j])

                    similarity = (intersection_size / (
                        song_i_users_count ** alpha * song_j_users_count ** (1 - alpha))) ** q
                    songs_similarity[song_i, song_j] = similarity
        else:
            sum_of_squares_for_song = [0] * self.songs_count
            for song_i in range(self.songs_count):
                sum_of_squares_for_song[song_i] = float((array[:, song_i] ** 2).sum(axis=0))


            for song_i in range(self.songs_count):
                song_i_sum_of_squares = sum_of_squares_for_song[song_i]
                for song_j in range(self.songs_count):
                    song_j_sum_of_squares = sum_of_squares_for_song[song_j]
                    dot_product = float((array[:, song_i] * array[:, song_j]).sum(axis=0))

                    similarity = (dot_product / (
                        song_i_sum_of_squares ** alpha * song_j_sum_of_squares ** (1 - alpha))) ** q
                    songs_similarity[song_i, song_j] = similarity

        return songs_similarity


    def get_scores_for_test_user(self, test_user: int, songs_similarity: np.ndarray) -> np.ndarray:
        scores = np.zeros(self.songs_count)
        known_songs_list = self.X_test[test_user].nonzero()[1].tolist()

        for known_song in known_songs_list:
            scores += songs_similarity[known_song] * float(self.X_test[test_user, known_song])

        return scores



    def calculate_MAP(self, alpha: float, q: float) -> float:
        songs_similarity = self.calculate_songs_similarity(alpha=alpha, q=q)

        sum_of_average_precisions = 0.0

        for test_user in range(self.test_size):
            scores = self.get_scores_for_test_user(test_user, songs_similarity)
            # todo: remove redundancy
            known_songs_list = self.X_test[test_user].nonzero()[1].tolist()

            known_songs_set = set(known_songs_list)

            # without known songs
            songs_with_scores = [(song, score) for song, score in enumerate(scores.tolist()) if
                                 song not in known_songs_set]
            songs_with_scores.sort(key=lambda pair: pair[1], reverse=True)

            relevant_songs = set(self.secret_songs[test_user])

            sum_of_precisions = 0.0
            current_relevant_count = 0
            for i in range(len(songs_with_scores)):
                song = songs_with_scores[i][0]
                if song in relevant_songs:
                    current_relevant_count += 1
                    sum_of_precisions += current_relevant_count / (i + 1)

            average_precision = sum_of_precisions / len(relevant_songs)
            sum_of_average_precisions += average_precision

        mean_average_precision = sum_of_average_precisions / self.test_size
        return mean_average_precision
