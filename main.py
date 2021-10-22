import nltk, re, pprint
from nltk import word_tokenize
from pathlib import Path


def test():
    articles_folder = Path('articles')
    if not articles_folder.is_dir():
        print("Articles directory not found. Aborting.")
        return
    article_files = articles_folder.glob('*.txt')
    articles_content = {}
    for i, file in enumerate(article_files):    # Debugging; load only one file
        if file.stem in ['111', '181', '199', '226', '247', '273', '282', '304', '390', '400', '428', '58', '6']:
            continue
        # print(file)
        with open(file) as f:
            articles_content[file.stem] = f.readlines()
    data = []
    with open('data.txt') as f:
        for line in f.readlines():
            data.append(line)
    a = articles_content[list(articles_content.keys())[0]][0]
    tokens = word_tokenize(a)
    b = nltk.pos_tag(tokens)
    a = 4
    # article = articles_content[articles_content.keys()[0]]





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test()
