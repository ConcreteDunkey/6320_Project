import csv

from nlp_solr import connect_solr
from answerer import SimpleNEAnswerer
from task1 import prep_output_dir, OUTPUT_DIR


def load_questions(question_file):
    with open(question_file) as q_file:
        res = q_file.read().splitlines()
    res = [i.replace('"', '') for i in res]
    return res


def do_task_3():
    output_file_name = 'NLP_QA.csv'
    questions = load_questions('new_question_list.txt')
    solr_core = connect_solr()
    method = SimpleNEAnswerer
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
    do_task_3()
