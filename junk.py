import ast
import random
import nltk, re, pprint
from nltk import word_tokenize
from rake_nltk import Rake
import pysolr
from nltk.stem import WordNetLemmatizer
# from pywsd.lesk import simple_lesk  # Broken ?
# Maybe.... ? from https://github.com/alvations/pywsd/blob/master/pywsd/utils.py#L129
from pathlib import Path
from main import load_articles, get_wn_pos


def junk():
    articles_folder = Path('articles')
    if not articles_folder.is_dir():
        print("Articles directory not found. Aborting.")
        return
    article_files = articles_folder.glob('*.txt')
    articles_content = {}
    for i, file in enumerate(article_files):    # Debugging; load only one file
        # if file.stem in ['111', '181', '199', '226', '247', '273', '282', '304', '390', '400', '428', '58', '6']:
        #     continue
        # print(file)
        with open(file, encoding='utf-8') as f:
            articles_content[file.stem] = f.readlines()
    #
    # solr_core = 'jim_core'
    # solr = pysolr.Solr('http://localhost:8983/solr/' + solr_core, always_commit=True, timeout=10)
    #
    # for article in articles_content:
    #     solr.add([{
    #         'id': article,
    #         'contents': articles_content[article]
    #     }])
    solr = load_articles()

    results = solr.search('contents:"rebels"')

    print("Saw {0} result(s).".format(len(results)))

    for result in results:
        print("The article id is '{0}'.".format(result['id']))

    data = []
    with open('data.txt', encoding='utf-8') as f:
        for line in f.readlines():
            data.append(line)
    # a is a list of words in one article

    a = articles_content[list(articles_content.keys())[0]][0]
    tokens = word_tokenize(a)
    # b is a, with POS tags
    b = nltk.pos_tag(tokens)
    # fd = nltk.FreqDist(tag for (word, tag) in b)
    # print(fd.most_common())
    # word_fd = nltk.FreqDist(b)
    # c = [wt[0] for (wt, _) in word_fd.most_common() if wt[1] == 'NNP']
    # print(c)
    word_net_lemmatizer = WordNetLemmatizer()
    # c = [word_net_lemmatizer.lemmatize(w, get_wn_pos(w)) for w in a]

    # c is lemmatized set of words in list a
    c = []
    for w in b:
        a = get_wn_pos(w[1])
        if a != '':
            c.append(word_net_lemmatizer.lemmatize(w[0], get_wn_pos(w[1])))
        else:
            c.append(w[0])
    a = 4
    # article = articles_content[articles_content.keys()[0]]