import pysolr
import time
from nlp_tools import art_pipeline
from pathlib import Path


class JimTimer:
    def __init__(self):
        self.prev = time.perf_counter()

    def lap(self):
        new = time.perf_counter()
        lap_time = new - self.prev
        self.prev = new
        return f"time:{lap_time:.04f}"


SOLR_CORE = 'solr_core'
solr_core = pysolr.Solr('dummy')
SolrTimer = JimTimer()


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
    SolrTimer.lap()
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
        print(f"Added article {article} after {SolrTimer.lap()}")
    solr_core.commit()


def build_solr_core():
    connect_solr()
    load_solr()


if __name__ == '__main__':
    build_solr_core()
