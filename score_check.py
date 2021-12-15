import numpy as np
import matplotlib.pyplot as plt
from answerer import \
    ScoreCheckAnswerer
from answerer_iterative import \
    SimpleLassoAnswerer
from nlp_solr import connect_solr
from training_test import import_q_a, all_q_a, test_q_a
from task1 import prep_output_dir, OUTPUT_DIR
import scipy.stats as st

# SAVE_PLOT = True
SAVE_PLOT = False
PLOT_LABEL = None


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
    old_scores_list = [corr_art_scores, incorr_art_scores, corr_sent_scores, incorr_sent_scores]
    labels_list = ["sents T", "sents F", "arts T", "arts F"]
    scores_list = []
    for scores in old_scores_list:
        scores_list.append(np.array(scores))
    tops = {labels_list[x]: top_scores(scores_list[x]) for x in range(len(scores_list))}
    deltas = {labels_list[x]: delta_scores(scores_list[x]) for x in range(len(scores_list))}

    print_score_statistics(tops, "top scores")
    print_score_statistics(deltas, "top two score deltas")

    # plot_score_boxplots(tops, "Top Scores, Random Question Subset (100)")
    # plot_score_boxplots(deltas, "Top Two Scores Delta, Random Question Subset (100)")

    # plot_score_boxplots(tops, "Top Scores, All Questions")
    # plot_score_boxplots(deltas, "Top Two Scores Delta, All Questions")
    return correct_art, correct_sent


def delta_scores(scores):
    if len(scores) > 0:
        res = scores[:, 0] - scores[:, 1]
    else:
        res = [0]
    return res


def top_scores(scores):
    if len(scores) > 0:
        res = scores[:, 0]
    else:
        res = [0]
    return res


def print_score_statistics(scores_dict, scores_type_str):
    summary = {}
    for key in scores_dict:
        _key = key.replace(' ', '_')
        summary[_key] = {'mean': np.mean(scores_dict[key]),
                         'sd': np.std(scores_dict[key]),
                         'n': len(scores_dict[key])}
        # # Following for easier human reading
        # print("For {} {}, mean {:.2f}, sd {:.2f}".format(scores_type_str,
        #                                                  key,
        #                                                  summary[_key]['mean'],
        #                                                  summary[_key]['sd']))
        # Following for easier machine reading
        print("{} {}, {:.2f}, {:.2f}".format(scores_type_str,
                                             key,
                                             summary[_key]['mean'],
                                             summary[_key]['sd']))

        # # The following statistics are currently non-functional
        # key_types = []
        # for key in summary.keys():
        #     if key.rsplit('_', 1)[0] not in key_types:
        #         key_types.append(key.rsplit('_', 1)[0])
        # for key_type in key_types:
        #     t_label = key_type + ' T'
        #     f_label = key_type + ' F'
        #     t_scores = scores_dict[t_label]
        #     f_scores = scores_dict[f_label]
        #     t = st.ttest_ind(t_scores, f_scores, equal_var=False)
        #     alpha = 0.99
        #     t_interval = st.t.interval(alpha=alpha, df=len(t_scores) - 1,
        #                                loc=np.mean(t_scores),
        #                                scale=st.sem(t_scores))
        #     f_interval = st.t.interval(alpha=alpha, df=len(f_scores) - 1,
        #                                loc=np.mean(f_scores),
        #                                scale=st.sem(f_scores))
        # Disregard pycharm warning in following line
        # print("Test that intervals are the same, for {} {}, "
        #       "p-value is {:2e}".format("articles" if key_type == "arts" else "sentences",
        #                                 scores_type_str,
        #                                 t.pvalue))
        # print("With alpha={}, score interval for correct answers is {:.2f} to {:.2f},"
        #       " score interval for incorrect answers is {:.2f} to {:.2f}.".format(alpha,
        #                                                                           t_interval[0],
        #                                                                           t_interval[1],
        #                                                                           f_interval[0],
        #                                                                           f_interval[1]))


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
        output_filename = 'boxplot ' + label.replace(',', '-') + '.pdf'
        output_file = out_dir / output_filename
        plt.savefig(output_file)
    plt.show()


def test():
    solr_core = connect_solr()
    test_only = True
    # test_only = False
    test_num_q = 100
    test_seed = 1
    methods = [{'class': ScoreCheckAnswerer,
                'label': "RAKE Keywords"},
               {'class': SimpleLassoAnswerer.single_l1,
                'label': "Lasso Keywords, Level 1"},
               {'class': SimpleLassoAnswerer.single_l2,
                'label': "Lasso Keywords, Level 2"},
               {'class': SimpleLassoAnswerer.single_l3,
                'label': "Lasso Keywords, Level 3"},
               {'class': SimpleLassoAnswerer.single_l4,
                'label': "Lasso Keywords, Level 4"},
               {'class': SimpleLassoAnswerer.single_l5,
                'label': "Lasso Keywords, Level 5"},
               {'class': SimpleLassoAnswerer.single_l6,
                'label': "Lasso Keywords, Level 6"},
               {'class': SimpleLassoAnswerer.single_l7,
                'label': "Lasso Keywords, Level 7"}
               ]
    q_a = import_q_a('data.txt')
    # q_a = import_q_a('new_data.txt')
    all_questions = all_q_a(q_a)

    for this_method in methods:
        print(this_method['label'])
        method = this_method['class']
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
