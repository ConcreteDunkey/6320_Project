#  Basic Answerer classes
import copy
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
        self.art_args = {
            'hl': 'true',
            'rows': 30,
            'fl': '*,score'}
        self.sent_args = {
            'hl': 'true',
            'rows': 30,
            'fl': '*,score'}
        # print('From __init__ in base Answerer class')

    def answer(self, question):
        results = self.this_method(question)
        if len(results) == 0:
            raise Exception("No results returned!")  # TODO FIXME
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
        return self.solr.search(question, **self.art_args)


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


# Take a question, return either "who", "what", or "when"
def determine_question_type(question):
    quest_words = ["when", "what", "who"]  # NOTE: List is prioritized based on analysis of question words
    res = None
    for quest_word in quest_words:
        if quest_word in question.lower():
            res = quest_word
    if res is None:
        raise Exception("No question word found in question.")
    return res


# From
# https://towardsdatascience.com/explorations-in-named-entity-recognition-and-was-eleanor-roosevelt-right-671271117218
#
# PERSON:      People, including fictional.
# NORP:        Nationalities or religious or political groups.
# FAC:         Buildings, airports, highways, bridges, etc.
# ORG:         Companies, agencies, institutions, etc.
# GPE:         Countries, cities, states.
# LOC:         Non-GPE locations, mountain ranges, bodies of water.
# PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
# EVENT:       Named hurricanes, battles, wars, sports events, etc.
# WORK_OF_ART: Titles of books, songs, etc.
# LAW:         Named documents made into laws.
# LANGUAGE:    Any named language.
# DATE:        Absolute or relative dates or periods.
# TIME:        Times smaller than a day.
# PERCENT:     Percentage, including ”%“.
# MONEY:       Monetary values, including unit.
# QUANTITY:    Measurements, as of weight or distance.
# ORDINAL:     “first”, “second”, etc.
# CARDINAL:    Numerals that do not fall under another type.
#
# Get possible named entity types based on question type
def get_NE_types(q_type):
    if q_type == 'who':
        res = ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE']
    elif q_type == 'what':
        res = ['NORP', 'FAC', 'ORG', 'GPE',
               'LOC', 'PRODUCT', 'WORK_OF_ART',
               'LAW', 'LANGUAGE', 'PERCENT', 'MONEY',
               'QUANTITY', 'ORDINAL', 'CARDINAL']
    elif q_type == 'when':
        res = ['DATE', 'TIME', 'EVENT']
    else:
        raise Exception("Question type not defined")
    return res


class SimpleNEAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)

    def this_method(self, question):
        keywords = self.keyword_method(question)
        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381
        prefix = '(contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ') type:"sentence" '
        results = self.def_search(query)
        q_type = determine_question_type(question)
        ne_types = get_NE_types(q_type)
        if q_type != "what":
            results_copy = copy.deepcopy(results)
            results.docs = []
            for result_doc in results_copy.docs:
                if hasattr(result_doc, 'named_entity'):
                    for entity in result_doc.named_entity:
                        entity_class = entity.split('_')[-1]
                        if entity_class in ne_types:
                            results.docs.append(result_doc)
                            break
            if len(results.docs) == 0:
                results = results_copy
        return results


class ArtRefineAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)

    def this_method(self, question):
        keywords = self.keyword_method(question)
        # The following line is needed to remove quotation marks from the search string
        # from https://stackoverflow.com/a/3939381
        prefix = '(contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ') AND type:"art" '
        results = self.def_search(query)
        q_type = determine_question_type(question)
        ne_types = get_NE_types(q_type)
        score = []
        for res in results:
            score.append(res['score'])
        print(score)
        return results


class ScoreCheckAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    keyword_method = staticmethod(get_single_keywords)

    def this_method(self, question):
        keywords = self.keyword_method(question)
        prefix = '(contents:"'
        postfix = '"'
        infix = '" OR contents:"'
        keyword_string = prefix + infix.join(keywords) + postfix
        query = keyword_string
        query += ') AND type:"sentence" '
        results = self.def_search(query)
        scores = []
        for res in results.docs[0:2]:
            scores.append(res['score'])
        # print(scores)
        return results, scores

    def answer(self, question):
        results, scores = self.this_method(question)
        if len(results) == 0:
            raise Exception("No results returned!")  # TODO FIXME
        art = results.docs[0]['id']
        if art.split('_')[1] == '0':
            sentence = ''
        else:
            sentence = results.docs[0]['contents'][0]
        art = art.split('_')[0]
        return art, sentence, scores


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
        # print(synonyms)
        spacied = NLP(question)
        ner_list = []
        for word in spacied.ents:
            ner_list.append(word.text +'_'+ word.label_)

        keywords = keywords + synonyms

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
        # print(score)

        return results
