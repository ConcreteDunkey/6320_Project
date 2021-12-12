from nlp_solr import load_articles
from nlp_tools import get_sentences


# Adds oracular answers for all questions to q_a dataset
# Turns out this is unneeded, but worth retaining.
def oracle(q_a):
    articles = load_articles()
    zero_answers = 0
    multi_answers = 0
    for article in articles:
        a = articles[article]
        article_sent = get_sentences(articles[article])
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
