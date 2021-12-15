import csv
import sys
from nlp_solr import connect_solr
from answerer import SingleKeywordAnswerer
from answerer_iterative import CompoundLassoAnswererFinal
from article_answers import Art_answerer
from task1 import prep_output_dir, OUTPUT_DIR
from sentence_ranking import get_sentence_given_question


def load_questions(question_file):
    with open(question_file) as q_file:
        res = q_file.read().splitlines()
    res = [i.replace('"', '') for i in res]
    return res


def do_task_2_sentence_ranking(output_file_name, questions_file):
    # output_file_name = 'NLP_QA.csv'
    questions = load_questions(questions_file)
    solr_core = connect_solr()
    results = []
    for question in questions:
        res_art, res_sent, _, _ = get_sentence_given_question(question)
        results.append([question, res_art, res_sent])
    out_dir = prep_output_dir(OUTPUT_DIR)
    output_file = out_dir / output_file_name
    with open(output_file, 'w', newline='', encoding='utf-8') as data_file:
        csv_writer = csv.writer(data_file, delimiter=',')
        for result in results:
            csv_writer.writerow(result)


def do_task_3(output_file_name, questions_file, algo):
    # output_file_name = output_file_name
    questions = load_questions(questions_file)
    solr_core = connect_solr()
    if algo == '1':
        method = SingleKeywordAnswerer
    else:  # algo == '2':
        method = CompoundLassoAnswererFinal

    answerer = method(solr_core)
    results = []
    for question in questions:
        res_art, res_sent = answerer.answer(question)
        results.append([question, res_art, res_sent])
    out_dir = prep_output_dir(OUTPUT_DIR)
    output_file = out_dir / output_file_name
    with open(output_file, 'w', newline='', encoding='utf-8') as data_file:
        csv_writer = csv.writer(data_file, delimiter=',')
        for result in results:
            csv_writer.writerow(result)


if __name__ == '__main__':
    # Algo 1: SingleKeywordAnswerer
    # Algo 2: CompoundLassoAnswererFinal
    # Algo 3: Sentence_Ranking
    if len(sys.argv) == 1:
        input_file = "new_question_list.txt"
        output_file = "NLP_QA.csv"
        algo = '3'
        print("Using default settings")
    elif len(sys.argv) == 4:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        algo = sys.argv[3]
    else:
        print("Please input 3 arguments or no arguments")
        print("Argument 1: input question file")
        print("Arguemnt 2: Output file name")
        print("Argument 3: model you want to run (1: RAKE keywords, 2: Query side, 3: Python side)")
        sys.exit(0)

    if (algo == '1') or (algo == '2'):
        do_task_3(output_file, input_file, algo)

    elif algo == '3':
        do_task_2_sentence_ranking(output_file, input_file)
