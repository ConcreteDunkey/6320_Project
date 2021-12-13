#  Basic Answerer classes
import pysolr
from rake_nltk import Rake
from nlp_tools import get_lemmas, get_nyms, get_nym, get_tokens, get_tagged_text
import spacy
NLP = spacy.load("en_core_web_sm")


class Answerer:
    def __init__(self, solr):
        if type(self) is Answerer:
            raise Exception('This is an abstract class and should not be instantiated.')
        self.solr = solr
        self.args = {
            'hl': 'true',
            'rows': 30,
            'fl': '*,score'}
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

    def search(self, question, args):
        return self.solr.search(question, **args)

    def def_search(self, question):
        return self.solr.search(question, **self.args)


class BadAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)
        # print('From __init__ in Bad_Answerer')

    def this_method(self, question):
        # This is a deliberately BAD search; pulling the first sentence it finds
        query = 'type:"sentence"'
        # return self.solr.search(query)
        return self.def_search(query)


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
        results = self.def_search(query)
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
        results = self.def_search(query)
        return results

class ArticleEnhancedAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)

    def get_all_nyms(self, lemmatized_text):
        nym_types = ['synonyms']
        res = {}
        for nym_type in nym_types:
            res[nym_type] = []
        for lemma in lemmatized_text:
            nyms = get_nyms(lemma, nym_types)
            for nym_type in nym_types:
                res[nym_type].extend(nyms[nym_type])
        return res

    def this_method(self, question):
        # keywords = self.keyword_method(question)
        keywords = get_tokens(question)
        tagged_text = get_tagged_text(keywords)
        lemmatized_text = get_lemmas(tagged_text)
        synonyms = self.get_all_nyms(lemmatized_text)['synonyms']
        synonyms = list(set(synonyms))
        print(synonyms)
        spacied = NLP(question)
        ner_list = []
        for word in spacied.ents:
            ner_list.append(word.text +'_'+ word.label_)

        # keywords = keywords + synonyms

        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381

        prefix = '(contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix

        prefix_ner = '(named_entity:"'
        postfix_ner = '"'
        infix_ner = '" OR named_entity:"'
        keyword_string_ner = prefix_ner + infix_ner.join(ner_list) + postfix_ner


        query = '(' + keyword_string + ')' + ' OR ' + keyword_string_ner + ')'
        query += ') AND type:"art" '

        results = self.def_search(query)

        score = []
        for res in results:
            score.append(res['score'])
        print(score)

        return results
