"""Reproducing some simple name-matching experiments to make sure the
code is working.
"""


import json
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer


def load(filename, a, b):
    with open(filename) as fp:
        obj = json.load(fp)
    a, b = obj[a], obj[b]
    return a, b

if __name__ == '__main__':
    # a pipeline to evaluate a particular softjoin
    # in secondstring format
    a0, b0 = load('id-parks.json', 'ic', 'nps')
    #a0, b0 = load('business.json', 'hw', 'it')
    print(f'loaded {len(a0["name"])} and {len(b0["name"])} names')
    vectorizer = TfidfVectorizer(stop_words='english')
    corpus = a0['name'] + b0['name']
    ab = vectorizer.fit_transform(corpus)
    # split out a and b
    num_a = len(a0['name'])
    a, b = ab[0:num_a], ab[num_a:]
    # compute TFIDF scores of all pairs
    sims = a.dot(b.T)
    # get best match to each thing in a (the rows)
    best_index = sims.argmax(1)
    best_score = sims.max(1).todense()
    
    # assess results
    df_rows = []
    for i in range(num_a):
        j = best_index[i,0]
        sim_ij = best_score[i,0]
        correct = 1 if a0['url'][i] == b0['url'][j] else 0
        df_rows.append(
            dict(a_name=a0['name'][i],
                 b_name=b0['name'][j],
                 sim=sim_ij,
                 a_url=a0['url'][i],
                 b_url=b0['url'][j],
                 correct=correct))
    df = pd.DataFrame(df_rows).sort_values(by='sim', ascending=False)
    
    hi = 1.0
    for lo in [0.999, 0.85, 0.7, 0.6, 0.5, -0.001]:
        close_matches = df[np.logical_and(df.sim > lo, df.sim <= hi)]
        print(f'{lo} < score <= {hi}:\ttotal {len(close_matches):2} acc={close_matches.correct.mean():.4f}')
        hi = lo
        
    print()
    exact_matches = df[df.sim == 1.0]
    print("Exact match errors:")
    print(exact_matches[exact_matches.correct==0])    

