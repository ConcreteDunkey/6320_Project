import random
import ast
import copy
from answerer import \
    BadAnswerer, \
    KeywordAnswerer, \
    SingleKeywordAnswerer, \
    SingleKeywordWithBlacklistAnswerer, \
    SimpleNEAnswerer, \
    ArtRefineAnswerer
from nlp_solr import connect_solr


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


def count_correctly_answered_questions(questions, solr_core, method, detailed_results=False):
    a = method(solr_core)
    correct_art = 0
    correct_sent = 0
    # questions = questions[9:]  # Easy way to skip ahead to a particular questions
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


def test():
    solr_core = connect_solr()
    # test_only = True
    test_only = False
    test_num_q = 100
    test_seed = 0
    # method = BadAnswerer
    # method = KeywordAnswerer
    # method = SingleKeywordAnswerer
    # method = SingleKeywordWithBlacklistAnswerer
    method = SimpleNEAnswerer
    # method = ArtRefineAnswerer

    q_a = import_q_a('data.txt')
    # q_a = import_q_a('new_data.txt')
    all_questions = all_q_a(q_a)

    if test_only:
        test_questions = test_q_a(all_questions, num_q=test_num_q, seed=test_seed)
        question_set = test_questions
        correct_art, correct_sent = count_correctly_answered_questions(question_set,
                                                                       solr_core,
                                                                       method,
                                                                       detailed_results=True)
    else:
        question_set = all_questions
        correct_art, correct_sent = count_correctly_answered_questions(question_set,
                                                                       solr_core,
                                                                       method,
                                                                       detailed_results=False)
    print(f"Of {len(question_set)} total questions, "
          f"the correct article was found {correct_art} times "
          f"and the correct sentence was found {correct_sent} times.")


if __name__ == '__main__':
    test()
