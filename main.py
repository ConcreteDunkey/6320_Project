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


def load_articles():
    articles_folder = Path('articles')
    if not articles_folder.is_dir():
        print("Articles directory not found. Aborting.")
        return
    article_files = articles_folder.glob('*.txt')
    articles_content = {}
    for i, file in enumerate(article_files):
        with open(file, encoding='utf-8') as f:
            articles_content[file.stem] = f.readlines()

    solr_core = 'jim_core'
    solr = pysolr.Solr('http://localhost:8983/solr/' + solr_core, always_commit=True, timeout=10)

    for article in articles_content:
        solr.add([{
            'id': article,
            'contents': articles_content[article]
        }])
    return solr


def import_q_a(q_a_file):
    q_a_dict = {}
    with open(q_a_file, encoding='utf-8') as f:
        raw_content = f.readlines()
    for row in raw_content:
        raw_line = list(ast.literal_eval(row))
        q_a_dict[raw_line[0]] = raw_line[1]
    return q_a_dict


def test_q_a(q_a_dict, num_q, seed):
    random.seed(seed)
    source_articles = random.sample(list(q_a_dict.keys()), num_q)
    test_q_a_list = []
    for source in source_articles:
        num_src_q = len(q_a_dict[source])
        q_num = random.randint(0, num_src_q)
        test_q_a_list.append({'q': q_a_dict[source][q_num][0],
                              'article': source,
                              'a': q_a_dict[source][q_num][1]})
    return test_q_a_list


def get_keywords(question):
    rake = Rake()
    rake.extract_keywords_from_text(question)
    keys_extracted = rake.get_ranked_phrases()
    return keys_extracted


def answer_question(question, solr):
    keywords = get_keywords(question)
    results = solr.search(f'contents:"{0}"'.format(' '.join(keywords)))
    # print("Saw {0} result(s).".format(len(results)))
    # for result in results:
    #     print("The article id is '{0}'.".format(result['id']))
    return results


def answer_questions(questions, solr):
    for question in questions:
        res = answer_question(question['q'], solr)
        res_list = []
        for result in res:
            res_list.append(result['id'])
        print(f"Expected article {question['article']}, got article {' '.join(res_list)}")


if __name__ == '__main__':
    index = load_articles()
    q_a = import_q_a('data.txt')
    test_questions = test_q_a(q_a, num_q=5, seed=0)
    answer_questions(test_questions, index)
    a = 5
    # test()
