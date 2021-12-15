from answerer import Answerer, get_single_keywords
from nltk.corpus import stopwords
from nlp_tools import \
    find_all_quotations_with_mark, \
    get_tokens, \
    NLP, \
    lazy_flatten_tree, \
    lazy_tree

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


def key_huer(question):
    # some of these are guesses...
    keep_np_pos = ['ADJ', 'ADP', 'ADV', 'NOUN', 'NUM', 'PROPN', 'VERB',
                   '$', '#', 'CD', 'FW', 'JJ', 'JJR', 'JJS', 'MD', 'NN', 'NNP',
                   'NNPS', 'NNS', 'RB', 'RBR', 'RBS', 'RP', "VB", "VBD", "VBG",
                   "VBN", "VBP", "VBZ", 'ADD', 'GW']
    stop_np_pos = []
    keep_vp_pos = ['ADP', 'ADV', 'VERB', 'MD', 'RB', 'RBR', 'RBS', 'RP', "VB",
                   "VBD", "VBG", "VBN", "VBP", "VBZ", 'GW']
    stop_vp_pos = ['NOUN', 'NN', 'NNP', 'NNPS', 'NNS', 'ADJ', 'PROPN', 'JJ',
                   'JJR', 'JJS', '.', 'WP', '#']
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
    # Level 8 (focus)
    huer_keys.append(find_clause_root_and_mods(tree, 'pobj', keep_np_pos, stop_np_pos))
    return huer_keys


def new_keywords(keys_so_far, maybe_new_keys):
    actually_new_keys = []
    for key in maybe_new_keys:
        if key not in keys_so_far:
            actually_new_keys.append(key)
    return actually_new_keys


def lasso_keywords(question, level):
    keywords_by_level = key_huer(question)
    keywords = []
    for i in range(len(keywords_by_level)):
        if i == level:
            break
        keywords.extend(new_keywords(keywords, keywords_by_level[i]))
    return keywords


def lasso_keywords_alt(question, levels):
    keywords_by_level = key_huer(question)
    keywords = []
    for i in range(len(keywords_by_level)):
        if i+1 in levels:
            keywords.extend(new_keywords(keywords, keywords_by_level[i]))
    return keywords


class IterativeAnswerer(Answerer):
    def __init__(self, solr):
        super().__init__(solr)

    # keyword_method = staticmethod(lasso_keywords)
    keyword_method = staticmethod(lasso_keywords_alt)

    def this_method(self, question):
        levels = [7]
        keywords = self.keyword_method(question, levels)
        # keywords = self.keyword_method(question, 2)
        # keywords = self.keyword_method(question)
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
