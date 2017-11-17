from pprint import pprint
from typing import List

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from sklearn.model_selection import train_test_split
import random
import time
from pandas import DataFrame

from data_loading import get_dataset
from item_based_filtering import ItemBasedFiltering
from user_based_filtering import UserBasedFiltering


random.seed("music")

# alpha = 0.5
# q = 1
test_proportion = 0.2
minimum_songs_per_user = 2
songs_count = 1000
users_count = 1000


start_time = time.time()

dataset = get_dataset(users_count, songs_count, minimum_songs_per_user, make_binary=False, make_log=True)

print("Data sparsity:", dataset.count_nonzero() / (dataset.shape[0] * dataset.shape[1]))

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

item_based_filtering = ItemBasedFiltering(X_train, X_test, secret_songs, data_is_binary=False)

from_q_and_alpha_to_MAP = DataFrame(None, index=[1, 2, 3, 4, 5],
                                    columns=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], dtype=np.float64)

for q in [1, 2, 3, 4, 5]:
    for alpha in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        MAP = item_based_filtering.calculate_MAP(alpha=alpha, q=q)
        print("alpha = {0}, q = {1}, MAP = {2:.6f}".format(alpha, q, MAP))
        from_q_and_alpha_to_MAP.loc[q, alpha] = MAP
        print("--- %s seconds ---" % (time.time() - start_time))

    print()

from_q_and_alpha_to_MAP.to_csv("results.csv", float_format="%.6f")

