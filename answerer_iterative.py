import nltk

from answerer import Answerer, get_single_keywords
from nltk.corpus import stopwords
from nlp_tools import find_all_quotations_with_mark, get_tokens, get_tagged_text


stop_words = set(stopwords.words('english'))


def find_all_quotations(question):
    res = []
    quotes = find_all_quotations_with_mark(question, '\"')
    if len(quotes) > 0:
        res = quotes
    else:
        quotes = find_all_quotations_with_mark(question, "\'")
        if len(quotes) > 0:
            res = quotes
    return res


def key_huer1(question):
    quotes = find_all_quotations(question)
    keywords_found = []
    for quote in quotes:
        tokens = get_tokens(quote)
        keywords_found.extend([w for w in tokens if not w.lower() in stop_words])
    if '?' in keywords_found:
        keywords_found.remove('?')
    return keywords_found


def key_huer2(question):
    tokens = get_tokens(question)
    tagged = get_tagged_text(tokens)
    keywords_found = [w for w , pos in tagged if pos == 'NNP']
    return keywords_found


# def key_huer3(question):
#


def lasso_keywords(question, level):
    keywords = []
    if level > 0:
        keywords.extend(key_huer1(question))
    return keywords


class IterativeAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    # keyword_method = staticmethod(lasso_keywords)
    keyword_method = staticmethod(key_huer2)

    def this_method(self, question):
        # keywords = self.keyword_method(question, 1)
        keywords = self.keyword_method(question)
        if len(keywords) > 0:
            print(question)
            print(keywords)
        # prefix = '(contents:"'
        # postfix = '"'
        # infix = '" OR contents:"'
        # keyword_string = prefix + infix.join(keywords) + postfix
        # query = keyword_string
        # query += ') AND type:"sentence" '
        # # results = self.def_search(query)
        results = {'docs': []}
        scores = []
        # for res in results.docs[0:2]:
        #     scores.append(res['score'])
        # print(scores)
        return results, scores

    def answer(self, question):
        results, scores = self.this_method(question)
        art = 0
        sentence = ''
        # if len(results) == 0:
        #     art = 0
        #     sentence = ''
        #     scores = [0, 0]
        # elif len(results) == 1:
        #     art = results.docs[0]['id']
        #     if art.split('_')[1] == '0':
        #         sentence = ''
        #     else:
        #         sentence = results.docs[0]['contents'][0]
        #     art = art.split('_')[0]
        #     scores = [scores[0], 0]
        # else:
        #     art = results.docs[0]['id']
        #     if art.split('_')[1] == '0':
        #         sentence = ''
        #     else:
        #         sentence = results.docs[0]['contents'][0]
        #     art = art.split('_')[0]
        # return art, sentence, scores
        return art, sentence
