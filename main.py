import ast
import random
import nltk
import re
import pprint
from rake_nltk import Rake
import pysolr
from nltk.stem import WordNetLemmatizer
# from pywsd.lesk import simple_lesk  # Broken ?
# Maybe.... ? from https://github.com/alvations/pywsd/blob/master/pywsd/utils.py#L129
from pathlib import Path


SOLR_CORE = 'jim_core'


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


def start_solr():
    solr_core = SOLR_CORE
    solr = pysolr.Solr('http://localhost:8983/solr/' + solr_core, always_commit=True, timeout=10)
    return solr


def load_articles():
    articles_folder = Path('articles')
    if not articles_folder.is_dir():
        print("Articles directory not found. Aborting.")
        return
    article_files = articles_folder.glob('*.txt')
    articles_content = {}
    for i, file in enumerate(article_files):
        with open(file, encoding='utf-8') as f:
            content = f.readlines()
            articles_content[file.stem] = ' '.join(content)
    return articles_content


def load_solr(solr):
    articles_content = load_articles()
    for article in articles_content:
        art_pipelined = pipeline(article)
        solr.add([{
            'id': article,
            'contents': articles_content[article]
        }])


def pipeline(article):
    sentences = nltk.sent_tokenize(article)
    tokens = nltk.word_tokenize(article)
    tagged_text = nltk.pos_tag(tokens)
    word_net_lemmatizer = WordNetLemmatizer()
    lemmatized_text = []
    for w in tagged_text:
        a = get_wn_pos(w[1])
        if a != '':
            lemmatized_text.append(word_net_lemmatizer.lemmatize(w[0], get_wn_pos(w[1])))
        else:
            lemmatized_text.append(w[0])
    a = 6
    return a


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


def all_q_a(q_a_dict):
    source_articles = q_a_dict.keys()
    q_a_list = []
    for source in source_articles:
        num_src_q = len(q_a_dict[source])
        for q_num in range(num_src_q):
            q_a_list.append({'q': q_a_dict[source][q_num][0],
                             'article': source,
                             'a': q_a_dict[source][q_num][1]})
    return q_a_list


def get_keywords(question):
    rake = Rake()
    rake.extract_keywords_from_text(question)
    keys_extracted = rake.get_ranked_phrases()
    return keys_extracted


def answer_question(question, solr):
    keywords = get_keywords(question)
    # keywords = ['Canadian', 'Alberta']
    prefix = 'contents:"'
    postfix = '"'
    infix = '" OR contents:"'
    keyword_string = prefix + infix.join(keywords) + postfix
    query = keyword_string
    results = solr.search(query)
    return results


def answer_questions(questions, solr):
    for question in questions:
        res = answer_question(question['q'], solr)
        res_list = []
        for result in res:
            res_list.append(result['id'])
        print(f"Expected article {question['article']}, got article {' '.join(res_list)}")


def oracle(q_a):
    articles = load_articles()
    zero_answers = 0
    multi_answers = 0
    for article in articles:
        a = articles[article]
        article_sent = nltk.sent_tokenize(articles[article])
        for i, question in enumerate(q_a):
            if str(question['article']) != article:
                continue
            count = a.count(question['a'])
            if count == 1:
                q_a[i]['o'] = [s for s in article_sent if question['a'] in s]
            elif count == 0:
                zero_answers += 1
            else:
                q_a[i]['o'] = [s for s in article_sent if question['a'] in s]
                multi_answers += 1
    return q_a


def test():
    index = start_solr()
    articles_not_loaded = False  # TODO Write something to determine if articles are loaded
    if articles_not_loaded:
        load_articles(index)
    q_a = import_q_a('data.txt')
    # test_questions = test_q_a(q_a, num_q=5, seed=0)
    all_questions = all_q_a(q_a)
    all_answers = oracle(all_questions)
    # answer_questions(test_questions, index)
    a = 5
    # test()


if __name__ == '__main__':
    test()
