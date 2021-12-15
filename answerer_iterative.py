from answerer import Answerer, get_single_keywords
from nltk.corpus import stopwords
from nlp_tools import \
    find_all_quotations_with_mark, \
    get_tokens, \
    NLP, \
    lazy_flatten_tree, \
    lazy_tree
# from score_check import delta_scores

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


def rec_find_depth_of_clauses(root, stop_pos_tags):
    res = {'token': root['token'],
           'pos': root['pos'],
           'dep': root['dep'],
           'lemma': root['lemma']}
    if 'children' in root:
        res['children'] = []
        for child in root['children']:
            if child['pos'] not in stop_pos_tags:
                res['children'].append(rec_find_depth_of_clauses(child, stop_pos_tags))
    return res


def rec_find_clauses(root, find_dep_tag, stop_pos_tags):
    res = []
    if root['dep'] == find_dep_tag:
        res = rec_find_depth_of_clauses(root, stop_pos_tags)
    elif 'children' in root:
        for child in root['children']:
            temp = rec_find_clauses(child, find_dep_tag, stop_pos_tags)
            if len(temp) > 0:
                if type(temp) is list:
                    res.extend(temp)
                else:
                    res.append(temp)
    return res


def find_clause_root_and_mods(tree, find_dep_tag, keep_pos, stop_pos_tags):
    keys = []
    clauses = rec_find_clauses(tree, find_dep_tag, stop_pos_tags)
    if type(clauses) is dict:
        clauses = [clauses]
    for clause in clauses:
        flat_clause = lazy_flatten_tree(clause)
        keys.extend([(token['lemma']) for token in flat_clause if token['pos'] in keep_pos])
    return keys


keep_np_pos = ['ADJ', 'ADP', 'ADV', 'NOUN', 'NUM', 'PROPN', 'VERB',
               '$', '#', 'CD', 'FW', 'JJ', 'JJR', 'JJS', 'MD', 'NN', 'NNP',
               'NNPS', 'NNS', 'RB', 'RBR', 'RBS', 'RP', "VB", "VBD", "VBG",
               "VBN", "VBP", "VBZ", 'ADD', 'GW']
stop_np_pos = []
keep_vp_pos = ['ADP', 'ADV', 'VERB', 'MD', 'RB', 'RBR', 'RBS', 'RP', "VB",
               "VBD", "VBG", "VBN", "VBP", "VBZ", 'GW']
stop_vp_pos = ['NOUN', 'NN', 'NNP', 'NNPS', 'NNS', 'ADJ', 'PROPN', 'JJ',
               'JJR', 'JJS', '.', 'WP', '#']


def key_huer(question):
    # some of these are guesses...
    huer_keys = []
    # Level 1
    huer_keys.append(key_huer1(question))
    # Level 2
    spacied = NLP(question)
    sentences = [sent for sent in spacied.sents]
    tree = lazy_tree(sentences[0].root)
    flat_tree = lazy_flatten_tree(tree)
    huer_keys.append([w['token'] for w in flat_tree if w['pos'] == 'NNP'])
    # Level 3 (nsub and modifiers??)
    huer_keys.append(find_clause_root_and_mods(tree, 'nsubj', keep_np_pos, stop_np_pos))
    # Level 4 (dobj and modifiers??)
    huer_keys.append(find_clause_root_and_mods(tree, 'dobj', keep_np_pos, stop_np_pos))
    # Level 5 (iobj and modifiers??)
    huer_keys.append(find_clause_root_and_mods(tree, 'iobj', keep_np_pos, stop_np_pos))
    # Level 6 (pobj and modifiers??)
    huer_keys.append(find_clause_root_and_mods(tree, 'pobj', keep_np_pos, stop_np_pos))
    # Level 7 (verbs)
    huer_keys.append(find_clause_root_and_mods(tree, 'ROOT', keep_vp_pos, stop_vp_pos))
    # # Level 8 (focus)
    # huer_keys.append(find_clause_root_and_mods(tree, 'pobj', keep_np_pos, stop_np_pos))
    return huer_keys


def new_keywords(keys_so_far, maybe_new_keys):
    actually_new_keys = []
    for key in maybe_new_keys:
        if key not in keys_so_far:
            actually_new_keys.append(key)
    return actually_new_keys


def condense_lasso_keywords(keywords_by_level, level):
    keywords = []
    for i in range(len(keywords_by_level)):
        if i == level:
            break
        keywords.extend(new_keywords(keywords, keywords_by_level[i]))
    return keywords


def lasso_keywords(question, level):
    keywords_by_level = key_huer(question)
    keywords = condense_lasso_keywords(keywords_by_level, level)
    return keywords


def lasso_keywords_alt(question, levels):
    keywords_by_level = key_huer(question)
    keywords = []
    for i in range(len(keywords_by_level)):
        if i+1 in levels:
            keywords.extend(new_keywords(keywords, keywords_by_level[i]))
    return keywords


def make_and_query(keywords):
    return make_a_query(keywords, "AND")


def make_or_query(keywords):
    return make_a_query(keywords, "OR")


def make_a_query(keywords, q_type):
    prefix = '(contents:"'
    postfix = '"'
    infix = f'" {q_type} contents:"'
    keyword_string = prefix + infix.join(keywords) + postfix
    query = keyword_string
    query += ') AND type:"sentence" '
    return query


class SimpleLassoAnswerer(Answerer):
    def __init__(self, solr, max_level=6, levels=None):
        super().__init__(solr)
        self.simple_lasso_levels = levels
        self.simple_lasso_level = max_level
        if levels is None:
            # self.keyword_method = staticmethod(lasso_keywords)
            self.keyword_method = lasso_keywords
        else:
            # self.keyword_method = staticmethod(lasso_keywords_alt)
            self.keyword_method = lasso_keywords_alt

    @classmethod
    def basic(cls, solr):
        return cls(solr)

    @classmethod
    def single_lvl(cls, solr, max_level):
        return cls(solr, max_level)

    @classmethod
    def single_l1(cls, solr):
        return cls(solr, max_level=1)

    @classmethod
    def single_l2(cls, solr):
        return cls(solr, max_level=2)

    @classmethod
    def single_l3(cls, solr):
        return cls(solr, max_level=3)

    @classmethod
    def single_l4(cls, solr):
        return cls(solr, max_level=4)

    @classmethod
    def single_l5(cls, solr):
        return cls(solr, max_level=5)

    @classmethod
    def single_l6(cls, solr):
        return cls(solr, max_level=6)

    @classmethod
    def single_l7(cls, solr):
        return cls(solr, max_level=7)

    @classmethod
    def many_lvl(cls, solr, levels):
        return cls(solr, levels=levels)

    def this_keyword_grabber(self, question):
        if self.simple_lasso_levels is None:
            return self.keyword_method(question, self.simple_lasso_level)
        else:
            return self.keyword_method(question, self.simple_lasso_levels)

    def this_method(self, question):
        keywords = self.this_keyword_grabber(question)
        # if len(keywords) > 0:
        #     print(question)
        #     print(keywords)
        query = make_and_query(keywords)
        results = self.def_search(query)
        # results = {'docs': []}  # For debugging; return empty
        scores = []
        for res in results.docs[0:2]:
            scores.append(res['score'])
        # print(scores)  # For debugging; print top 2 scores
        return results, scores

    def answer(self, question):
        results, scores = self.this_method(question)
        art, sentence, scores = make_scorable_results(results, scores)
        return art, sentence, scores


def make_scorable_results(results, scores):
    if len(results) == 0:
        art = 0
        sentence = ''
        scores = [0, 0]
    elif len(results) == 1:
        art = results.docs[0]['id']
        if art.split('_')[1] == '0':
            sentence = ''
        else:
            sentence = results.docs[0]['contents'][0]
        art = art.split('_')[0]
        scores = [scores[0], 0]
    else:
        scores = scores[0:2]
        art = results.docs[0]['id']
        if art.split('_')[1] == '0':
            sentence = ''
        else:
            sentence = results.docs[0]['contents'][0]
        art = art.split('_')[0]
    return art, sentence, scores


def delta_scores(scores):
    if len(scores) > 1:
        res = scores[0] - scores[1]
    elif len(scores) == 1:
        res = scores[0]
    else:
        res = [0]
    return res


class CompoundLassoAnswerer(Answerer):
    # def __init__(self, solr, max_level=6, levels=None):
    def __init__(self, solr, max_level=6):
        super().__init__(solr)
        # self.simple_lasso_levels = levels
        self.simple_lasso_level = max_level
        # if levels is None:
        #     self.keyword_method = lasso_keywords
        # else:
        #     self.keyword_method = lasso_keywords_alt

    # @classmethod
    # def basic(cls, solr):
    #     return cls(solr)
    #
    # @classmethod
    # def single_lvl(cls, solr, max_level):
    #     return cls(solr, max_level)
    #
    # @classmethod
    # def single_l1(cls, solr):
    #     return cls(solr, max_level=1)
    #
    # @classmethod
    # def single_l2(cls, solr):
    #     return cls(solr, max_level=2)
    #
    # @classmethod
    # def single_l3(cls, solr):
    #     return cls(solr, max_level=3)
    #
    # @classmethod
    # def single_l4(cls, solr):
    #     return cls(solr, max_level=4)
    #
    # @classmethod
    # def single_l5(cls, solr):
    #     return cls(solr, max_level=5)
    #
    # @classmethod
    # def single_l6(cls, solr):
    #     return cls(solr, max_level=6)
    #
    # @classmethod
    # def single_l7(cls, solr):
    #     return cls(solr, max_level=7)
    #
    # @classmethod
    # def many_lvl(cls, solr, levels):
    #     return cls(solr, levels=levels)
    #
    # def this_keyword_grabber(self, question):
    #     if self.simple_lasso_levels is None:
    #         return self.keyword_method(question, self.simple_lasso_level)
    #     else:
    #         return self.keyword_method(question, self.simple_lasso_levels)

    def this_method(self, question):
        all_keywords = key_huer(question)
        flag = 0
        while 1 == 1:
            keywords = condense_lasso_keywords(all_keywords, 6)
            query = make_and_query(keywords)
            results = self.def_search(query)
            scores = []
            for res in results.docs[0:20]:
                scores.append(res['score'])
            if len(scores) > 0:
                if scores[0] > 10:
                    flag = 1
                    break
                # a = scores[0]
                # b = delta_scores(scores)
                # if len(scores)>1 and scores[0] > 7.5 and delta_scores(scores) > 4.5:
                #     flag = 2
                #     break
            # if len(scores) > 0 and scores[0] > 2:
            #     break
            scores = []
            for res in results.docs[0:2]:
                scores.append(res['score'])
            results = []
            break
        return results, scores, flag

    def answer(self, question):
        results, scores, flag = self.this_method(question)
        art, sentence, scores = make_scorable_results(results, scores)
        return art, sentence, (scores, flag)
