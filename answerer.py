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


def get_single_keywords_with_blacklist(question):
    keys_extracted = get_keywords(question)
    blacklist = ["one", "type"]
    single_keywords = []
    for key in keys_extracted:
        subkeys = key.split()
        for subkey in subkeys:
            if subkey in blacklist:
                continue
            single_keywords.append(subkey)
    return single_keywords


class KeywordAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in KeywordAnswerer')

    keyword_method = staticmethod(get_keywords)

    def this_method(self, question):
        keywords = self.keyword_method(question)
        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381
        prefix = 'contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ' type:"sentence"'
        results = self.solr.search(query, **{
                'hl': 'true',
                'rows': 30,
                'fl': '*,score'
            })
        return results


class SingleKeywordAnswerer(KeywordAnswerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in KeywordAnswerer')

    keyword_method = staticmethod(get_single_keywords)

    def this_method(self, question):
        results = super().this_method(question)
        return results


class SingleKeywordWithBlacklistAnswerer(KeywordAnswerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in KeywordAnswerer')

    keyword_method = staticmethod(get_single_keywords_with_blacklist)

    def this_method(self, question):
        results = super().this_method(question)
        return results


class SimpleNEAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)

    def this_method(self, question):
        keywords = self.keyword_method(question)
        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381
        prefix = 'contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ' type:"sentence" '
        results = self.solr.search(query)
        return results
