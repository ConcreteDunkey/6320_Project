import nltk
import spacy
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
# import training_test as tt
# from answerer import determine_question_type


NLP = spacy.load("en_core_web_sm")


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


def art_pipeline(article):
    sentences = get_sentences(article)
    tokens = get_tokens(article)
    tagged_text = get_tagged_text(tokens)
    lemmatized_text = get_lemmas(tagged_text)
    named_entities, _ = get_named_entities_and_parse_trees(article)
    return sentences, tokens, tagged_text, lemmatized_text, named_entities


def all_pipeline(text):
    sentences = get_sentences(text)
    tokens = get_tokens(text)
    tagged_text = get_tagged_text(tokens)
    lemmatized_text = get_lemmas(tagged_text)
    nyms = get_all_nyms(lemmatized_text)
    named_entities, parse_trees = get_named_entities_and_parse_trees(text)
    return sentences, tokens, tagged_text, lemmatized_text, nyms, parse_trees, named_entities


def get_sentences(article):
    sentences = nltk.sent_tokenize(article)
    return sentences


def get_tokens(article):
    tokens = nltk.word_tokenize(article)
    return tokens


def get_tagged_text(tokens):
    tagged_text = nltk.pos_tag(tokens)
    return tagged_text


def get_lemmas(tagged_text):
    word_net_lemmatizer = WordNetLemmatizer()  # TODO: Make this a global, test if it runs faster
    lemmatized_text = []
    for w in tagged_text:
        a = get_wn_pos(w[1])
        if a != '':
            lemmatized_text.append(word_net_lemmatizer.lemmatize(w[0], get_wn_pos(w[1])))
        else:
            lemmatized_text.append(w[0])
    return lemmatized_text


# Can be full article or single sentence
def get_named_entities_and_parse_trees(text):
    spacied = NLP(text)
    parse_trees = []
    for sentence in spacied.sents:
        parse_trees.append(lazy_tree(sentence.root))
    ner_list = []
    for word in spacied.ents:
        # Workaround of old method
        ner_list.append(word.text +'_'+ word.label_)
        # Old method not working
        # ner_list.append((word.text, word.label_))
    return ner_list, parse_trees


def lazy_tree(root):
    res = lazy_tree_rec(root)
    return res


def lazy_tree_rec(node):
    res = {'token': str(node.orth_),
           'pos': str(node.tag_),
           'dep': str(node.dep_)}  # Dependency
    children = [x for x in node.children]
    if children:
        res['children'] = [lazy_tree_rec(x) for x in children]
    return res


def get_all_nyms(lemmatized_text):
    nym_types = ['hypernyms',
                 'hyponyms',
                 'part_meronyms',
                 'substance_meronyms',
                 'part_holonyms',
                 'substance_holonyms',
                 'entailments']
    res = {}
    for nym_type in nym_types:
        res[nym_type] = []
    for lemma in lemmatized_text:
        nyms = get_nyms(lemma, nym_types)
        for nym_type in nym_types:
            res[nym_type].extend(nyms[nym_type])
    return res


def get_nyms(lemma, nym_types):
    senses = wn.synsets(lemma)
    res = {}
    for nym_type in nym_types:
        res[nym_type] = []
    for sense in senses:
        for nym_type in nym_types:
            res[nym_type].extend(get_nym(sense, nym_type))
            a = 0  # TODO: clean this
    return res


def get_nym(sense, nym_type):
    res = []
    if hasattr(sense, nym_type):
        method_name = getattr(sense, nym_type)
        nyms = method_name()
        for synset in nyms:
            for word in synset.lemmas():
                res.append(word.name())
    elif nym_type =='synonyms':
        for synset in sense.lemmas():
            res.append(synset.name().replace("_"," "))
    return res


def quest_types(q_as):
    # quest_words = ["who", "what", "where", "when", "why", "how"]
    quest_words = ["who", "what", "when"]
    quest_words_ct = {}
    for word in quest_words:
        quest_words_ct[word] = 0
    first_quest_words_ct = Counter()
    for q_a in q_as:
        quest_words_in_this_question = 0
        words_in_this_quest = nltk.word_tokenize(q_a['q'].lower())
        first_quest_words_ct.update({q_a['q'].split()[0]: 1})
        for word in quest_words:
            if word in words_in_this_quest:
                quest_words_ct[word] += 1
                quest_words_in_this_question += 1
        if quest_words_in_this_question > 1:
            print(q_a)
        if 'how' in words_in_this_quest:
            pass
    return


def test():
    test_sentence = "I am curious about your analysis of different questions."
    q_a = tt.import_q_a('data.txt')
    # q_a = import_q_a('new_data.txt')
    all_questions = tt.all_q_a(q_a)
    for q_a in all_questions:
        question = q_a['q']
        determine_question_type(question)


if __name__ == '__main__':
    test()
