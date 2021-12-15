import spacy
import numpy as np
import ast
from nlp_solr import connect_solr
from article_answers import ArticleEnhancedAnswerer
import nltk
from nltk.corpus import wordnet as wn
NLP = spacy.load("en_core_web_sm")

def count_correctly_answered_questions(questions, detailed_results=False):
    correct_art = 0
    correct_sent = 0
    # questions = questions[9:]  # Easy way to skip ahead to a particular questions
    for question in questions:
        article, sentence, overlap_score, overlap_buffer = get_sentence_given_question(question['q'])
        res_art, res_sent = article, sentence

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

def get_sentence_given_question(question):
    method = ArticleEnhancedAnswerer
    solr_core = connect_solr()
    a = method(solr_core)
    ids, docs = a.answer(question)
    token_of_interest, ner_list = get_tokens_of_interest_given_a_question(question)
    article_, sentence_, overlap_score, overlap_buffer = get_best_overlap_score(ids, docs, token_of_interest, ner_list)

    return article_, sentence_, overlap_score, overlap_buffer


def get_tokens_of_interest_given_a_question(question):
    doc = NLP(question)
    token_of_interest = []
    dependency_candidates = ['nsubj', 'dobj', 'nobj', 'pobj', 'ROOT', 'acl', 'nummod','compound', 'amod', 'xcomp'
                          , "npadvmod", "acomp", "pcomp","conj","nsubjpass","poss", "attr", "advmod"]
    for token in doc:
        if token.dep_ in dependency_candidates and (token.is_stop!=True):
            token_of_interest.append(token.text)



    ner_list = []
    ner_label = []
    for ent in doc.ents:
        ner_list.append(ent.text)
        ner_label.append(ent.label_)

    return token_of_interest, ner_list


def get_best_overlap_score(ids, docs, token_of_interest, ner_list):
    overlap = 0
    article_id = -9999
    sentence = ""
    overlap_buffer = []
    if len(docs) == 0:
        return -999, "", -1, -1

    for i, doc in zip(ids, docs):
        for each_sent, each_sent_lemma in zip(doc[1], ' '.join(doc[2])):
            current_overlap = 0
            for token in token_of_interest:
                if (token.lower() in each_sent.lower()) or (token.lower() in each_sent_lemma.lower()) :
                    current_overlap += 1
            for ner_token in ner_list:
                if ner_token.lower() in each_sent.lower():
                    current_overlap += 1
            if current_overlap > overlap:
                overlap = current_overlap
                article_id = i
                sentence = each_sent
                overlap_buffer = []

            if current_overlap == overlap:
                overlap_buffer.append((i, each_sent, current_overlap))

    return (article_id, sentence, overlap, overlap_buffer)





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
        # print("returning empty")
        print("------------------------", tag)
        res = ''
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



if __name__ == '__main__':
    q_a = import_q_a('data.txt')
    all_questions = all_q_a(q_a)
    question_set =  all_questions[:50]
    correct_art, correct_sent = count_correctly_answered_questions(question_set, detailed_results=True)
    print(f"Of {len(question_set)} total questions, "
          f"the correct article was found {correct_art} times "
          f"and the correct sentence was found {correct_sent} times.")
