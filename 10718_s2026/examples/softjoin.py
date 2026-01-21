import fire
import json
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

from tabulate import tabulate
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer


def load_corpus(filename):
    with open(filename, 'r') as fp:
        return [line.strip() for line in fp.readlines()]

def softjoin(filename1, filename2):
    a0 = load_corpus(filename1)
    b0 = load_corpus(filename2)
    vectorizer = TfidfVectorizer(stop_words='english')
    ab = vectorizer.fit_transform(a0 + b0)
    # split out a and b from ab
    a, b = ab[0:len(a0)], ab[len(a0):]
    # compute TFIDF scores of all pairs
    start_time = time.time()
    print('joining...')
    sims = a.dot(b.T)
    elapsed = time.time() - start_time
    print(f'joined in {elapsed:.4f} sec')
    # get best match to each thing in a (the rows)
    best_index = sims.argmax(1)
    best_score = sims.max(1).todense()
    # return results
    return a0, b0, sims, best_index, best_score

def near_dups(a0, b0, sims, best_index, best_score, threshold=0.5, truncate=200):
    rows = []
    for i in range(len(a0)):
        j = best_index[i,0]
        sim_ij = best_score[i,0]
        if sim_ij > threshold:
            rows.append(dict(sim=sim_ij, i=i, a_i=a0[i][:truncate], j=j, b_j=b0[j][:truncate]))
    return pd.DataFrame(rows).sort_values(by='sim', ascending=False)

def dedup(filename1, filename2, threshold=0.4, truncate=200, maxcolwidths=50):
    df = near_dups(*softjoin(filename1, filename2), threshold=threshold, truncate=truncate)
    print(tabulate(df, maxcolwidths=maxcolwidths))
    
if __name__ == '__main__':
    fire.Fire()
