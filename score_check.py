import numpy as np
import matplotlib.pyplot as plt
from answerer import \
    ScoreCheckAnswerer
from nlp_solr import connect_solr
from training_test import import_q_a, all_q_a, test_q_a


def count_correctly_answered_questions(questions, solr_core, method, detailed_results=False):
    a = method(solr_core)
    correct_art = 0
    correct_sent = 0
    corr_art_scores = []
    incorr_art_scores = []
    corr_sent_scores = []
    incorr_sent_scores = []
    for question in questions:
        res_art, res_sent, res_scores = a.answer(question['q'])
        if question['article'] == int(res_art):
            correct_art += 1
            corr_art_scores.append(res_scores)
        else:
            incorr_art_scores.append(res_scores)
        if question['a'] in res_sent:
            correct_sent += 1
            corr_sent_scores.append(res_scores)
        else:
            incorr_sent_scores.append(res_scores)
        # elif detailed_results:
        #     print(f"Predicted {int(res_art)}, actually {question['article']}.")
        #     print(f"   Question: {question['q']}")
        #     print(f"   Guessed answer sentence: {res_sent}")
        #     print(f"   Answer should contain: {question['a']}")
    plot_score_deltas(corr_sent_scores, "correct sentences")
    plot_score_deltas(incorr_sent_scores, "incorrect sentences")
    plot_score_deltas(corr_art_scores, "correct articles")
    plot_score_deltas(incorr_art_scores, "incorrect articles")
    return correct_art, correct_sent


def plot_score_deltas(scores, label):
    scores = np.array(scores)
    scores_delta = scores[:, 0] - scores[:, 1]
    fig = plt.figure(figsize=(5, 7))
    print("For {}, mean {:.2f}, sd {:.2f}".format(label,
                                                  np.mean(scores_delta),
                                                  np.std(scores_delta)))
    plt.title(label)
    plt.boxplot(scores_delta)
    plt.show()


def test():
    solr_core = connect_solr()
    test_only = True
    # test_only = False
    test_num_q = 100
    test_seed = 1
    method = ScoreCheckAnswerer

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
