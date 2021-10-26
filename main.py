import nltk, re, pprint
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
# from pywsd.lesk import simple_lesk  # Broken ?
# Maybe.... ? from https://github.com/alvations/pywsd/blob/master/pywsd/utils.py#L129
from pathlib import Path


def get_wn_pos(tag):
    res = None
    if tag.startswith('N'):
        res = nltk.corpus.wordnet.NOUN
    elif tag.startswith('V'):
        res = nltk.corpus.wordnet.VERB
    elif tag.startswith('J'):
        res = nltk.corpus.wordnet.ADJ
    elif tag.startswith('R'):
        res = nltk.corpus.wordnet.ADV
    else:
        res = ''
    return res


def test():
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
    data = []
    with open('data.txt', encoding='utf-8') as f:
        for line in f.readlines():
            data.append(line)
    a = articles_content[list(articles_content.keys())[0]][0]
    tokens = word_tokenize(a)
    b = nltk.pos_tag(tokens)
    fd = nltk.FreqDist(tag for (word, tag) in b)
    print(fd.most_common())
    word_fd = nltk.FreqDist(b)
    c = [wt[0] for (wt, _) in word_fd.most_common() if wt[1] == 'NNP']
    print(c)
    word_net_lemmatizer = WordNetLemmatizer()
    # c = [word_net_lemmatizer.lemmatize(w, get_wn_pos(w)) for w in a]
    c = []
    for w in b:
        a = get_wn_pos(w[1])
        if a != '':
            c.append(word_net_lemmatizer.lemmatize(w[0], get_wn_pos(w[1])))
        else:
            c.append(w[0])

    a = 4
    # article = articles_content[articles_content.keys()[0]]





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test()
