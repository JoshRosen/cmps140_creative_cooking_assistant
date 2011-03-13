import nltk
from nltk.corpus import wordnet

from nlu.stanford_utils import is_in_conjunct
from nlu.stanford_utils import is_in_disjunct
from nlu.stanford_utils import get_parse_tree

def is_word_in_conjunct(parse_tree, word):
    """
    >>> import nltk
    >>> raw_input_string = "What can I make with carrots and children?"
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> tree = get_parse_tree(tokenized_string)
    >>> print is_word_in_conjunct(tree, 'children')
    True
    """
    for node in parse_tree.getLeaves():
        if node.value() == word:
            return is_in_conjunct(parse_tree, node)
    return None
    
def is_word_in_disjunct(parse_tree, word):
    """
    >>> import nltk
    >>> raw_input_string = "What can I make with carrots or children and cellary?"
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> tree = get_parse_tree(tokenized_string)
    >>> print is_word_in_disjunct(tree, 'carrots')
    True
    """
    for node in parse_tree.getLeaves():
        if node.value() == word:
            return is_in_disjunct(parse_tree, node)
    return None
    
def extract_close_keywords(keywords, tokenized_string, minDistance):
    """
    >>> raw_input_string = 'I like fish.'
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> keywords = ['like.v.05']
    >>> extract_close_keywords(keywords, tokenized_string, 2)
    ['like']
    """
    closeWords = []
    for keyword in keywords:
        keywordSyn = wordnet.synset(keyword)
        for word in tokenized_string:
            for wordSyn in wordnet.synsets(word):
                distance = keywordSyn.shortest_path_distance(wordSyn)
                if distance != None and distance <= minDistance:
                    closeWords.append(word)
                    break
    return closeWords
    
def extract_words_from_list(word_list, string_list, enum=False):
    """
    Returns (index, word) or a list of words for words which occur in both
    lists.
    """
    
    for i, word in enumerate(string_list):
        if word in word_list:
            if enum:
                yield (i, word)
            else:
                yield word
                
def get_keyword_confidence(raw_input_string, keywords, minDistance):
    bestDistance = float('inf')

    tokenizer = nltk.WordPunctTokenizer()
    tokenized_string = tokenizer.tokenize(raw_input_string)

    # Find the best keyword synset distance to input string
    for keyword in keywords:
        keywordSyn = wordnet.synset(keyword)
        for word in tokenized_string:
            for wordSyn in wordnet.synsets(word):
                distance = keywordSyn.shortest_path_distance(wordSyn)
                if distance != None:
                    bestDistance = min(bestDistance, distance)
                
    if bestDistance <= minDistance:
        return (1-(float(bestDistance)/minDistance)) * .5 + .5
    else:
        return 0.0
