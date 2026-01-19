import ast
import fire
import math
import matplotlib.pyplot as plt
import sys

from collections import Counter
from nltk.corpus import stopwords
from wordcloud import WordCloud

def load_text(filename):
    """Text in a file."""
    with open(filename) as fp:
        return fp.read()

def word_count(filename):
    """Count of non-stopwords in a file."""
    stopword = set(stopwords.words('english'))
    ctr = Counter([
        token.lower()
        for token in load_text(filename).split()
        if token not in stopword])
    return ctr

def cmp_counts(filename1, filename2):
    """Differences in wordcounts."""
    def score(n1,n2): 
        return math.log((n1 + 1.0)/(n1 + n2 + 2.0))
    wc1 = word_count(filename1)
    wc2 = word_count(filename2)
    common_words = set(wc1) & set(wc2)
    return {w: score(wc1[w], wc2[w]) for w in common_words}

def make_freqcloud(freq):
    cloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        min_font_size=10
    ).generate_from_frequencies(freq)
    return cloud

def make_wordcloud(text):
    cloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        min_font_size=10
    ).generate(text)
    return cloud

def plot_cloud(cloud):
    plt.figure(figsize=(10, 5))
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis("off") # Turn off the axes and tick marks
    plt.show()

def cloud(corpus_filename):
    """Wordcloud for a corpus.
    """
    plot_cloud(make_wordcloud(load_text(corpus_filename)))

def cmp_cloud(filename1, filename2):
    """Wordcloud comparing two corpora.
    """
    plot_cloud(make_freqcloud(cmp_counts(filename1, filename2)))

def blue():
    cloud('bluecorpus.txt')

def red():
    cloud('redcorpus.txt')

def blue_v_red():
    """DailyKos with words weighted by #(word in blue) / #(word in red + blue)
    """
    cmp_cloud('bluecorpus.txt', 'redcorpus.txt')

def red_v_blue():
    """DailyKos with words weighted by 1 - (#(word in blue) / #(word in red + blue))
    """
    cmp_cloud('redcorpus.txt', 'bluecorpus.txt')

def jordan_vs_sutton():
    cmp_cloud('ai-the-revolution.txt', 'bitter-lesson.txt')

def sutton_vs_jordan():
    cmp_cloud('bitter-lesson.txt', 'ai-the-revolution.txt')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fire.Fire()

