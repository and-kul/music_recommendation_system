import numpy as np
from scipy.sparse import csr_matrix
from typing import List

from item_based_filtering import ItemBasedFiltering
from user_based_filtering import UserBasedFiltering


class CombinedFiltering:
    def __init__(self, X_train: csr_matrix, X_test: csr_matrix, secret_songs: List[List[int]], data_is_binary: bool,
                 alpha_for_user_based: float, q_for_user_based: float,
                 alpha_for_item_based: float, q_for_item_based: float):
        if not data_is_binary:
            raise Exception("only binary data supported")
        self.data_is_binary = data_is_binary
        self.secret_songs = secret_songs
        self.train_size = X_train.shape[0]
        self.test_size = X_test.shape[0]
        self.songs_count = X_train.shape[1]

        self.X_test = X_test

        self.user_based_filtering = UserBasedFiltering(X_train, X_test, secret_songs, data_is_binary)
        self.item_based_filtering = ItemBasedFiltering(X_train, X_test, secret_songs, data_is_binary)

        users_similarity = self.user_based_filtering.calculate_users_similarity(alpha_for_user_based, q_for_user_based)
        songs_similarity = self.item_based_filtering.calculate_songs_similarity(alpha_for_item_based, q_for_item_based)

        self.users_similarity = users_similarity
        self.songs_similarity = songs_similarity


    def calculate_MAP(self, gamma) -> float:
        """
        :param gamma: gamma * user_based_score + (1-gamma) * item_based
        """
        sum_of_average_precisions = 0.0

        for test_user in range(self.test_size):
            user_based_scores = self.user_based_filtering.get_scores_for_test_user(test_user, self.users_similarity)
            item_based_scores = self.item_based_filtering.get_scores_for_test_user(test_user, self.songs_similarity)

            scores = user_based_scores * gamma + item_based_scores * (1 - gamma)

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




