import numpy as np
import matplotlib.pyplot as plt
from answerer import \
    ScoreCheckAnswerer
from nlp_solr import connect_solr
from training_test import import_q_a, all_q_a, test_q_a
from task1 import prep_output_dir, OUTPUT_DIR


SAVE_PLOT = True
# SAVE_PLOT = False


def count_correctly_answered_questions(questions, solr_core, method, detailed_results=False):
    a = method(solr_core)
    correct_art = 0
    correct_sent = 0
    corr_art_scores = []
    incorr_art_scores = []
    corr_sent_scores = []
    incorr_sent_scores = []
    # for question in questions:
    for i, question in enumerate(questions):
        # if i < 1313:
        #     continue
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
    old_scores_list = [corr_art_scores, incorr_art_scores, corr_sent_scores, incorr_sent_scores]
    labels_list = ["sents T", "sents F", "arts T", "art F"]
    scores_list = []
    for scores in old_scores_list:
        scores_list.append(np.array(scores))
    tops = {labels_list[x]: top_scores(scores_list[x]) for x in range(len(scores_list))}
    deltas = {labels_list[x]: delta_scores(scores_list[x]) for x in range(len(scores_list))}

    print_score_statistics(tops, "top scores")
    print_score_statistics(deltas, "top two score deltas")
    # plot_score_boxplots(tops, "Top Scores, Random Question Subset (100)")
    # plot_score_boxplots(deltas, "Top Two Scores Delta, Random Question Subset (100)")
    plot_score_boxplots(tops, "Top Scores, All Questions")
    plot_score_boxplots(deltas, "Top Two Scores Delta, All Questions")
    return correct_art, correct_sent


def delta_scores(scores):
    return scores[:, 0] - scores[:, 1]


def top_scores(scores):
    a = scores[:, 0]
    return scores[:, 0]


def print_score_statistics(scores_dict, scores_type_str):
    for key in scores_dict:
        print("For {} {}, mean {:.2f}, sd {:.2f}".format(scores_type_str,
                                                         key,
                                                         np.mean(scores_dict[key]),
                                                         np.std(scores_dict[key])))


def plot_score_boxplots(scores_dict, label):
    fig, ax = plt.subplots()
    pos = np.arange(len(scores_dict)) + 1
    scores = scores_dict.values()
    fig = plt.title(label)
    bp = ax.boxplot(scores, sym='k+', positions=pos,
                    notch=1)
    # ax.set_xlabel('')
    ax.set_ylabel('solr Score')
    plt.xticks(pos, scores_dict.keys())
    plt.setp(bp['whiskers'], color='k', linestyle='-')
    plt.setp(bp['fliers'], markersize=3.0)
    if SAVE_PLOT:
        out_dir = prep_output_dir(OUTPUT_DIR)
        output_filename = 'boxplot ' + label.replace(',', '-')+'.pdf'
        output_file = out_dir / output_filename
        plt.savefig(output_file)
    plt.show()


def test():
    solr_core = connect_solr()
    # test_only = True
    test_only = False
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
