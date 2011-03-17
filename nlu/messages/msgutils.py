import nltk
from nltk.corpus import wordnet

from nlu.stanford_utils import get_parse_tree
from nlu.stanford_utils import extract_junction_node
from nlu.stanford_utils import get_node_string
from nlu.stanford_utils import extract_subject_nodes
from nlu.stanford_utils import extract_negation_nodes

def extract_subjects(parse_tree, enum=True):
    """
    Returns a list of subject words.
    """
    for node in extract_subject_nodes(parse_tree):
        word = get_node_string(node)
        if enum:
            yield (parse_tree.indexOf(node), word)
        else:
            yield word

def is_negated(parse_tree, word):
    """
    
    >>> import nltk
    >>> raw_input_string = "I don't want ugly fish."
    >>> tokenizer = nltk.TreebankWordTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> tree = get_parse_tree(tokenized_string)
    >>> is_negated(tree, 'fish')
    True
    >>> is_negated(tree, 'want')
    True
    
    >>> raw_input_string = "I like the color of this text but not its putrid smell."
    >>> tokenizer = nltk.TreebankWordTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> tree = get_parse_tree(tokenized_string)
    >>> is_negated(tree, 'smell')
    True
    >>> is_negated(tree, 'color')
    False
    >>> is_negated(tree, 'cats') == None
    True
    """
    # locate the word node
    for node in parse_tree.getLeaves():
        if node.value() == word:
            # extract the word node
            nodes = extract_negation_nodes(parse_tree, node)
            # return type of negation
            # TODO: do more advanced detection of negation
            if nodes: # found negation nodes
                return True
            else: # no negation nodes found
                return False
    return None

def extract_junction(parse_tree, word):
    """
    Returns either 'and' or 'or'. Defaults to 'and' if junction cannot be
    determined.
    
    >>> import nltk
    >>> raw_input_string = "What can I make with carrots and children or celery?"
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> tree = get_parse_tree(tokenized_string)
    >>> extract_junction(tree, 'carrots')
    'and'
    >>> extract_junction(tree, 'children')
    'and'
    >>> extract_junction(tree, 'celery')
    'or'
    >>> extract_junction(tree, 'rats') == None
    True
    """
    # locate the word node
    for node in parse_tree.getLeaves():
        if node.value() == word:
            # extract the junction node
            node = extract_junction_node(parse_tree, node)
            # return the node junction type
            if node:
                nodeString = get_node_string(node)
                if 'and' in nodeString:
                    return 'and'
                elif 'or' in nodeString:
                    return 'or'
            else:
                return 'and'
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
