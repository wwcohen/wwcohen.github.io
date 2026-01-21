"""Examples of soft joins and deduping with TFIDF.
"""

import fire
import pandas as pd
import numpy as np
import time

from tabulate import tabulate

from sklearn.feature_extraction.text import TfidfVectorizer

def load_corpus(filename: str) -> list[str]:
    """Returns all lines in a file.
    """
    with open(filename, 'r') as fp:
        return [line.strip() for line in fp.readlines()]

def tfidfsims(filename1:str, dedup:bool=False, filename2:str|None=None):
    """Return result of soft match or deduping.

    """
    assert dedup != (filename2 is not None), 'only use filename2 if dedup=False'

    a0 = load_corpus(filename1)
    b0 = a0 if dedup else load_corpus(filename2)
    # convert all lines in a0 and b0 to documents with TFIDF weights
    vectorizer = TfidfVectorizer(stop_words='english')
    ab = vectorizer.fit_transform(a0 + b0)
    # ab is a sparse matrix - split it into two, one for each of the
    # original corpora
    a, b = ab[0:len(a0)], ab[len(a0):]
    # compute TFIDF scores of all pairs: sim[i,j] is TFIDF similarity
    # of a[i] to b[j].
    start_time = time.time()
    print('joining...')
    sims = a.dot(b.T)
    elapsed = time.time() - start_time
    print(f'joined in {elapsed:.4f} sec')
    # get best match to each thing in a (the rows)
    if dedup:
        # discard self-matches and also redundant j > i by setting the
        # similarities to small values (but not zero, that messes with
        # the sparsity pattern
        for i in range(sims.shape[0]):
            sims[i, i:] = 0.00001
    # find the best match in each row and its score
    best_index = sims.argmax(1)
    best_score = sims.max(1).todense()
    # return results
    return a0, b0, sims, best_index, best_score

def near_dups(a0, b0, sims, best_index, best_score, threshold=0.5, truncate=200) -> pd.DataFrame:
    """Find 'near duplicates' - the bj that best matches each ai, dropping
    anything with a score less than threshold.  Documents are truncated to
    the first 'truncate' characters.
    """
    rows = []
    for i in range(len(a0)):
        j = best_index[i,0]
        sim_ij = best_score[i,0]
        if sim_ij > threshold:
            rows.append(dict(sim=sim_ij, i=i, a_i=a0[i][:truncate], j=j, b_j=b0[j][:truncate]))
    return pd.DataFrame(rows).sort_values(by='sim', ascending=False)

def softjoin(filename1, filename2, threshold=0.4, truncate=200, maxcolwidths=50):
    """Compare documents in filename1 to documents in filename2.
    """
    df = near_dups(*tfidfsims(filename1=filename1, filename2=filename2), threshold=threshold, truncate=truncate)
    print(tabulate(df, maxcolwidths=maxcolwidths))
    
def dedup(filename, threshold=0.4, truncate=200, maxcolwidths=50):
    """Compare all pairs of documents ai, aj for j>i in filename.
    """
    df = near_dups(*tfidfsims(filename1=filename, dedup=True), threshold=threshold, truncate=truncate)
    print(tabulate(df, maxcolwidths=maxcolwidths))

if __name__ == '__main__':
    fire.Fire()
