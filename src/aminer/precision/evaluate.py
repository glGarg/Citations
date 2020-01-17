import heapq
import json
import math
import os
import pickle
from os import listdir
from os.path import isfile

import numpy as np
import pkg_resources
import scipy
from gensim.models import FastText
from scipy import spatial

from aminer.recall.query_es import get_abstract_by_pids

root_directory = pkg_resources.resource_filename("aminer", "support")
model_directory = os.path.join(root_directory, "models")

vec = pickle.load(open(os.path.join(model_directory, 'vec.model'), 'rb'))
fasttext = FastText.load(os.path.join(model_directory, 'fasttext', 'fasttext.model'))
word_to_idx = list(vec.get_feature_names())


def compute_abstract_embedding(abstract):
    tfidf_vec = vec.transform([abstract])
    tfidf_vec = scipy.sparse.coo_matrix(tfidf_vec)
    word_count = 0
    sum_embedding = np.zeros(50)
    for _, word_index, word_tfidf in zip(tfidf_vec.row, tfidf_vec.col, tfidf_vec.data):
        word = word_to_idx[word_index]
        if word in fasttext.wv.vocab:
            word_count += 1
            sum_embedding += fasttext.wv[word]

    if word_count == 0:
        return [0] * 50

    return (sum_embedding / word_count).tolist()


def get_all_embeddings(current_embedding, files):
    for file in files:
        print("Checking file: ", file)
        with open(file, 'r') as f:
            embeddings = json.load(f)
            f.close()

        for id, emb in embeddings.items():
            cosine_similarity = 1 - spatial.distance.cosine(current_embedding, emb)
            if not math.isnan(cosine_similarity):
                yield (id, cosine_similarity)


def recommend(ids):
    ids_to_abstract = get_abstract_by_pids(ids)

    recommendations = {}

    for target_id, abstract in ids_to_abstract.items():
        print("Finding recommendations for: ", target_id)
        embeddings_directory = os.path.join(root_directory, "embeddings")

        current_embedding = compute_abstract_embedding(abstract)

        files = [os.path.join(embeddings_directory, f) for f in listdir(embeddings_directory) if isfile(os.path.join(embeddings_directory, f))]

        all_embeddings = get_all_embeddings(current_embedding, files)
        recommendations[target_id] = heapq.nlargest(100, all_embeddings, key=lambda e: e[1])

    return recommendations


if __name__ == '__main__':
    file = os.path.join(root_directory, 'ids.txt')
    ids = [line.rstrip('\n') for line in open(file)]

    recommendations = recommend(ids)

    outfile = os.path.join(root_directory, 'recommendations.json')

    with open(outfile, 'w') as f:
        json.dump(recommendations, f)








