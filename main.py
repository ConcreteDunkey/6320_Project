import ast
import copy
import random
import nltk
import re
import time
import pprint
import pysolr
import spacy
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from pathlib import Path
from answerer import \
    BadAnswerer, \
    KeywordAnswerer, \
    SingleKeywordAnswerer, \
    SingleKeywordWithBlacklistAnswerer, \
    SimpleNEAnswerer

NLP = spacy.load("en_core_web_sm")
SOLR_CORE = 'solr_core'
solr_core = pysolr.Solr('dummy')


class JimTimer:
    def __init__(self):
        self.prev = time.perf_counter()

    def lap(self):
        new = time.perf_counter()
        lap_time = new - self.prev
        self.prev = new
        return f"time:{lap_time:.04f}"


Timer = JimTimer()


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


def connect_solr():
    global solr_core
    solr_core = pysolr.Solr('http://localhost:8983/solr/' + SOLR_CORE, always_commit=False, timeout=10)
    return solr_core


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


def load_solr():
    global solr_core
    num_docs = 0  # Keep track of number of additions
    Timer.lap()
    articles_content = load_articles()
    for article in articles_content:
        sentences, tokens, tagged_text, lemmatized_text, ner_text = art_pipeline(articles_content[article])
        solr_core.add([{
            'id': article + "_0",
            'contents': articles_content[article],
            'type': 'art',
            'tokens': tokens,
            'tagged_text': tagged_text,
            'lemmatized_text': lemmatized_text,
            'named_entity': ner_text
        }])
        num_docs += 1
        for i, sentence in enumerate(sentences):
            _, tokens, tagged_text, lemmatized_text, ner_text = art_pipeline(sentence)
            solr_core.add([{
                'id': article + "_" + str(i + 1),
                'contents': sentence,
                'type': 'sentence',
                'tokens': tokens,
                'tagged_text': tagged_text,
                'lemmatized_text': lemmatized_text,
                'named_entity': ner_text
            }])
            num_docs += 1
        print(f"Added article {article} after {Timer.lap()}")
    solr_core.commit()


def art_pipeline(article):
    sentences = get_sentences(article)
    tokens = get_tokens(article)
    tagged_text = get_tagged_text(tokens)
    lemmatized_text = get_lemmas(tagged_text)
    # nyms = get_all_nyms(lemmatized_text)
    named_entities = get_named_entities(article)
    return sentences, tokens, tagged_text, lemmatized_text, named_entities


def all_pipeline(text):
    sentences = get_sentences(text)
    tokens = get_tokens(text)
    tagged_text = get_tagged_text(tokens)
    lemmatized_text = get_lemmas(tagged_text)
    nyms = get_all_nyms(lemmatized_text)
    named_entities = get_named_entities(text)
    return sentences, tokens, tagged_text, lemmatized_text, named_entities


def get_sentences(article):
    sentences = nltk.sent_tokenize(article)
    return sentences


def get_tokens(article):
    tokens = nltk.word_tokenize(article)
    return tokens


def get_tagged_text(tokens):
    tagged_text = nltk.pos_tag(tokens)
    return tagged_text


def get_lemmas(tagged_text):
    word_net_lemmatizer = WordNetLemmatizer()  # TODO: Make this a global, test if it runs faster
    lemmatized_text = []
    for w in tagged_text:
        a = get_wn_pos(w[1])
        if a != '':
            lemmatized_text.append(word_net_lemmatizer.lemmatize(w[0], get_wn_pos(w[1])))
        else:
            lemmatized_text.append(w[0])
    return lemmatized_text


def get_named_entities(article):
    spacied = NLP(article)
    for sentence in spacied.sents:
        parse_tree = lazy_tree(sentence.root)
        # for w in a:
        #     b = w
    ner_list = []
    for word in spacied.ents:
        ner_list.append((word.text, word.label_))
    return ner_list


def lazy_tree(root):
    res = lazy_tree_rec(root)
    return res


def lazy_tree_rec(node):
    res = {'token': str(node.orth_),
           'pos': str(node.tag_),
           'dep': str(node.dep_)}  # Dependency
    children = [x for x in node.children]
    if children:
        res['children'] = [lazy_tree_rec(x) for x in children]
    return res


def get_all_nyms(lemmatized_text):
    nym_types = ['hypernyms',
                 'hyponyms',
                 'part_meronyms',
                 'substance_meronyms',
                 'part_holonyms',
                 'substance_holonyms',
                 'entailments']
    res = {}
    for nym_type in nym_types:
        res[nym_type] = []
    for lemma in lemmatized_text:
        nyms = get_nyms(lemma, nym_types)
        for nym_type in nym_types:
            res[nym_type].extend(nyms[nym_type])
    return res


def get_nyms(lemma, nym_types):
    senses = wn.synsets(lemma)
    res = {}
    for nym_type in nym_types:
        res[nym_type] = []
    for sense in senses:
        for nym_type in nym_types:
            res[nym_type].extend(get_nym(sense, nym_type))
            a = 0
    return res


def get_nym(sense, nym_type):
    # senses = wn.synsets(lemma)
    res = []
    # for sense in senses:
    if hasattr(sense, nym_type):
        method_name = getattr(sense, nym_type)
        nyms = method_name()
        for synset in nyms:
            for word in synset.lemmas():
                res.append(word.name())
    return res


def import_q_a(q_a_file):
    q_a_dict = {}
    with open(q_a_file, encoding='utf-8') as f:
        raw_content = f.readlines()
    for row in raw_content:
        raw_line = list(ast.literal_eval(row))
        q_a_dict[raw_line[0]] = raw_line[1]
    return q_a_dict


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


def test_q_a(q_a, num_q, seed):
    random.seed(seed)
    test_q_a_list = copy.deepcopy(q_a)
    random.shuffle(test_q_a_list)
    return test_q_a_list[0: num_q]


def count_correctly_answered_questions(questions, method, detailed_results=False):
    a = method(solr_core)
    correct_art = 0
    correct_sent = 0
    for question in questions:
        res_art, res_sent = a.answer(question['q'])
        if question['article'] == int(res_art):
            correct_art += 1
        if question['a'] in res_sent:
            correct_sent += 1
        elif detailed_results:
            print(f"Predicted {int(res_art)}, actually {question['article']}.")
            print(f"   Question: {question['q']}")
            print(f"   Guessed answer sentence: {res_sent}")
            print(f"   Answer should contain: {question['a']}")
    return correct_art, correct_sent


# Adds oracular answers for all questions to q_a dataset
# Turns out this is unneeded, but worth retaining.
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


def quest_types(q_as):
    # quest_words = ["who", "what", "where", "when", "why", "how"]
    quest_words = ["who", "what", "when"]
    quest_words_ct = {}
    for word in quest_words:
        quest_words_ct[word] = 0
    first_quest_words_ct = Counter()
    # quest_words_ct = [0 for ]
    for q_a in q_as:
        quest_words_in_this_question = 0
        words_in_this_quest = nltk.word_tokenize(q_a['q'].lower())
        first_quest_words_ct.update({q_a['q'].split()[0]: 1})
        for word in quest_words:
            if word in words_in_this_quest:
                quest_words_ct[word] += 1
                quest_words_in_this_question += 1
        if quest_words_in_this_question > 1:
            print(q_a)
        if 'how' in words_in_this_quest:
            a = 4
    return


def test():
    all_pipeline("All the of his opponents' kids wishes he was their dad.")
    response = connect_solr()
    data_loaded = False  # TODO Write something to determine if articles are loaded
    # test_only = False
    test_only = True
    test_num_q = 100
    test_seed = 0
    # method = BadAnswerer
    # method = KeywordAnswerer
    # method = SingleKeywordAnswerer
    method = SingleKeywordWithBlacklistAnswerer
    # method = SimpleNEAnswerer

    if not data_loaded:
        load_solr()
    q_a = import_q_a('data.txt')
    all_questions = all_q_a(q_a)
    # oracle(all_questions)

    # quest_types(all_questions)

    if test_only:
        test_questions = test_q_a(all_questions, num_q=test_num_q, seed=test_seed)
        question_set = test_questions
        correct_art, correct_sent = count_correctly_answered_questions(question_set, method, detailed_results=True)
    else:
        question_set = all_questions
        correct_art, correct_sent = count_correctly_answered_questions(question_set, method, detailed_results=False)
    print(f"Of {len(question_set)} total questions, "
          f"the correct article was found {correct_art} times "
          f"and the correct sentence was found {correct_sent} times.")


if __name__ == '__main__':
    test()
