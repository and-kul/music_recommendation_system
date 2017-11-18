import numpy as np
from scipy.sparse import csr_matrix
from typing import List


class UserBasedFiltering:
    def __init__(self, X_train: csr_matrix, X_test: csr_matrix, secret_songs: List[List[int]], data_is_binary: bool):
        self.data_is_binary = data_is_binary
        self.X_train = X_train
        self.X_test = X_test
        self.secret_songs = secret_songs
        self.train_size = X_train.shape[0]
        self.test_size = X_test.shape[0]
        self.songs_count = X_train.shape[1]

    def calculate_users_similarity(self, alpha, q) -> np.ndarray:
        # from [test_user, train_user] to similarity
        users_similarity = np.zeros((self.test_size, self.train_size))

        if self.data_is_binary:
            for test_user in range(self.test_size):
                test_user_songs_count = self.X_test[test_user].count_nonzero()
                for train_user in range(self.train_size):
                    train_user_songs_count = self.X_train[train_user].count_nonzero()
                    intersection_size = self.X_test[test_user].multiply(
                        self.X_train[train_user]).count_nonzero()

                    similarity = (intersection_size / (
                        test_user_songs_count ** alpha * train_user_songs_count ** (1 - alpha))) ** q
                    users_similarity[test_user, train_user] = similarity
        else:
            for test_user in range(self.test_size):
                test_user_sum_of_squares = float(self.X_test[test_user].power(2).sum(axis=1))
                for train_user in range(self.train_size):
                    train_user_sum_of_squares = float(self.X_train[train_user].power(2).sum(axis=1))
                    dot_product = float(self.X_test[test_user].multiply(self.X_train[train_user]).sum(axis=1))

                    similarity = (dot_product / (
                        test_user_sum_of_squares ** alpha * train_user_sum_of_squares ** (1 - alpha))) ** q
                    users_similarity[test_user, train_user] = similarity

        return users_similarity


    def get_scores_for_test_user(self, test_user: int, users_similarity: np.ndarray) -> np.ndarray:
        scores = np.zeros(self.songs_count)
        for train_user in range(self.train_size):
            scores += (
                self.X_train[train_user].multiply(
                    users_similarity[test_user, train_user])).toarray().reshape(
                (self.songs_count,))
        return scores



    def calculate_MAP(self, alpha: float, q: float) -> float:
        users_similarity = self.calculate_users_similarity(alpha, q)

        sum_of_average_precisions = 0.0

        for test_user in range(self.test_size):
            scores = self.get_scores_for_test_user(test_user, users_similarity)

            known_songs = set(self.X_test[test_user].nonzero()[1].tolist())

            # without known songs
            songs_with_scores = [(song, score) for song, score in enumerate(scores.tolist()) if song not in known_songs]
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
