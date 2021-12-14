#  Basic Answerer classes
import copy
import pysolr
from rake_nltk import Rake
from nlp_tools import get_lemmas, get_nyms, get_nym, get_tokens, get_tagged_text
import spacy
from nlp_tools import get_lemmas, get_tagged_text
NLP = spacy.load("en_core_web_sm")



def get_keywords(question):
    rake = Rake()
    rake.extract_keywords_from_text(question)
    keys_extracted = rake.get_ranked_phrases()
    # Strip out ' and " so that we don't mess up solr:
    keys_extracted = [s.translate({ord(c): None for c in '\'\"?'}) for s in keys_extracted]
    keys_extracted = [s.strip() for s in keys_extracted]
    return keys_extracted


def get_single_keywords(question):
    keys_extracted = get_keywords(question)
    single_keywords = []
    for key in keys_extracted:
        subkeys = key.split()
        for subkey in subkeys:
            single_keywords.append(subkey)
    return single_keywords

def build_query(contents_or_other, keywords):

    prefix = '(' + contents_or_other+ ':"'
    postfix = '"'
    infix = '" OR ' + contents_or_other + ':"'
    keyword_string = prefix + infix.join(keywords) + postfix + ')'
    return keyword_string

def get_wn_pos(tag):
    res = None
    if tag.startswith('N'):
        res = nltk.corpus.wordnet.NOUN
    elif tag.startswith('V'):
        res = nltk.corpus.wordnet.VERB
    elif tag.startswith('J'):
        res = nltk.corpus.wordnet.ADJ
    elif tag.startswith('R'):
        res = nltk.corpus.wordnet.ADV
    else:
        res = ''
    return res


class Art_answerer:
    def __init__(self, solr):
        if type(self) is Art_answerer:
            raise Exception('This is an abstract class and should not be instantiated.')
        self.solr = solr
        self.art_args = {
            'hl': 'true',
            'rows': 30,
            'fl': 'id,contents,score'}

    def answer(self, question):
        results = self.this_method(question)
        if len(results) == 0:
            art = 0
            sentence = ''
        else:
            art = []
            sentence = []
            for results_each in results:

                single_art = results_each['id'].split('_')[0]
                # print(results_each['id'])
                art.append(single_art)
                # If we return the full article, the answer will be found within it.
                # if single_art[1] == '0':
                #     sentence = ''
                # else:
                sentence.append(results_each['contents'])
                # art = art.split('_')[0]
        return art, sentence

    def this_method(self, question):
        raise Exception('This is an abstract class and should not be instantiated.')
        return 2

    def search(self, question, args):
        return self.solr.search(question, **args)

    def def_search(self, question):
        return self.solr.search(question, **self.art_args)


class ArticleEnhancedAnswerer(Art_answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)


    def this_method(self, question):
        keywords = self.keyword_method(question)

        tagged_text = get_tagged_text(keywords)
        lemmatized_text = get_lemmas(tagged_text)

        q1 = build_query('contents', keywords)
        # print(q1)
        # q2 = build_query('tagged_text', tagged_text)
        q3 = build_query('lemmatized_text', lemmatized_text)
        # query = q1 + ' AND '+ q3 + ' AND type:"art"'
        query = q1 + ' AND type:"art"'
        # prefix = '(contents:"'
        # postfix = '"'
        # infix = '" OR contents:"'
        #
        # keyword_string = prefix + infix.join(keywords) + postfix
        # query = keyword_string
        # query += ') AND type:"art" '
        results = self.def_search(query)
        arr = results.docs[:5].copy()
        # print(query)
        # arr = [item for sublist in arr for item in sublist.copy()]

        # print(len(arr))

        # if len(results.docs)==0:
            # print("zero docs found")
        return results.docs[:5]
