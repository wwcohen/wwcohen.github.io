import ast
import fire
import math
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def load_text(filename):
    with open(filename) as fp:
        return fp.read()

def load_freq(filename, inv=False):
    freq = {}
    for line in open(filename):
        (a, b) = ast.literal_eval(line.strip())
        freq[a] = 1 - math.exp(b) if inv else math.exp(b)
    return freq

def make_freqcloud(freq):
    cloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        # stop_words is a set of words to ignore (e.g., 'the', 'a', 'is')
        #stopwords={'a', 'of', 'is', 'the', 'or', 'and', 'This', 'its'}, 
        min_font_size=10
    ).generate_from_frequencies(freq)
    return cloud

def make_wordcloud(text):
    cloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        # stop_words is a set of words to ignore (e.g., 'the', 'a', 'is')
        #stopwords={'a', 'of', 'is', 'the', 'or', 'and', 'This', 'its'}, 
        min_font_size=10
    ).generate(text)
    return cloud

def plot_cloud(cloud):
    plt.figure(figsize=(10, 5))
    plt.imshow(cloud, interpolation='bilinear')
    plt.axis("off") # Turn off the axes and tick marks
    plt.show()

def blue():
    """DailyKos corpus wordcloud.
    """
    plot_cloud(make_wordcloud(load_text('bluecorpus.txt')))

def blue_v_red():
    """DailyKos with words weighted by #(word in blue) / #(word in red + blue)
    """
    plot_cloud(make_freqcloud(load_freq('blue-red-cmp.txt')))

def red_v_blue():
    """DailyKos with words weighted by 1 - (#(word in blue) / #(word in red + blue))
    """
    plot_cloud(make_freqcloud(load_freq('blue-red-cmp.txt', inv=True)))

if __name__ == '__main__':
    fire.Fire()

