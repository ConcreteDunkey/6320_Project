from main import load_articles, all_pipeline
import json
import pathlib


def write_full_pipeline_result(text, file):
    with open(file, 'r', encoding='utf-8') as this_file:
        json_so_far = json.load(this_file)
    res = {}
    full_res = all_pipeline(text)
    res['sentences'],\
        res['tokens'],\
        res['POS_tags'],\
        res['lemmas'],\
        res['nyms'],\
        res['parse_trees'],\
        res['named_entities'] = full_res
    # parsed = json.loads(res)
    with open(file, 'w', encoding='utf-8') as this_file:
        json_so_far.append(res)
        json.dump(json_so_far, this_file, indent=4)


def load_questions():
    with open('question_list.txt') as q_file:
        res = q_file.read().splitlines()
    res = [i.replace('"', '') for i in res]
    return res


def prep_output_dir(out_dir):
    path = pathlib.Path(out_dir)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path


def prep_output_file(out_dir, out_file_name):
    out_file = out_dir / out_file_name
    with open(out_file, mode='w', encoding='utf-8') as f:
        json.dump([], f)
    return out_file


def task1():
    out_dir = prep_output_dir('output/')

    questions = load_questions()
    q_file = prep_output_file(out_dir, "NLP_pipeline_questions.json")
    for question in questions:
        write_full_pipeline_result(question, q_file)

    articles = load_articles()
    article = articles['111']
    article_file = prep_output_file(out_dir, "NLP_pipeline_article.json")
    write_full_pipeline_result(article, article_file)


if __name__ == '__main__':
    task1()