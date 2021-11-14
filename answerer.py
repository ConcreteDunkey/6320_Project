#  Basic Answerer classes
import pysolr
from rake_nltk import Rake


class Answerer:
    def __init__(self, solr):
        if type(self) is Answerer:
            raise Exception('This is an abstract class and should not be instantiated.')
        self.solr = solr
        # print('From __init__ in base Answerer class')

    def answer(self, question):
        results = self.this_method(question)
        art = results.docs[0]['id']
        # If we return the full article, the answer will be found within it.
        if art.split('_')[1] == '0':
            sentence = ''
        else:
            sentence = results.docs[0]['contents'][0]
        art = art.split('_')[0]
        return art, sentence

    def this_method(self, question):
        raise Exception('This is an abstract class and should not be instantiated.')
        return 2


class BadAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in Bad_Answerer')

    def this_method(self, question):
        # This is a deliberately BAD search; pulling the first sentence it finds
        query = 'type:"sentence"'
        return self.solr.search(query)


def get_keywords(question):
    rake = Rake()
    rake.extract_keywords_from_text(question)
    keys_extracted = rake.get_ranked_phrases()
    return keys_extracted


class KeywordAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in KeywordAnswerer')

    def this_method(self, question):
        keywords = get_keywords(question)
        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381
        keywords = [s.translate({ord(c): None for c in '\'\"?'}) for s in keywords]
        keywords = [s.strip() for s in keywords]
        prefix = 'contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ' type:"sentence"'
        results = self.solr.search(query)
        return results
