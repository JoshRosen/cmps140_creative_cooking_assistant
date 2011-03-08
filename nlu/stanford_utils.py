import os
import collections

from nlu.nluserver import *

# generate parser
_trainerFile = os.path.join(os.path.dirname(__file__), 'englishPCFG.ser.gz')
lexical_parser = LexicalizedParser(_trainerFile)

def _iterator_first(iterator):
    try:
        return iterator.next()
    except StopIteration:
        return None

def get_parse_tree(tokenized_string, lexical_parser=lexical_parser):
    """
    Generates a java parse tree from a tokenized string.
    
    >>> import nltk
    >>> raw_input_string = "Two by two, hands of blue."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> print get_parse_tree(tokenized_string) #doctest: +NORMALIZE_WHITESPACE
    (ROOT (NP [51.609] (NP [9.479] (CD [5.183] Two)) (PP [10.542] (IN [3.812]
    by) (NP [6.303] (CD [2.852] two))) (, [0.000] ,) (NP [24.495] (NP [9.513]
    (NNS [6.958] hands)) (PP [14.189] (IN [0.612] of) (NP [13.150] (NN [11.011]
    blue)))) (. [0.013] .)))
    """
    # build up the java array
    stringArray = ArrayList()
    for word in tokenized_string: stringArray.append(word)
    # parse and return
    lexical_parser.parse(stringArray)
    return lexical_parser.getBestParse()

def get_nodes_by_type(parse_tree, node_type):
    """
    returns a tree tagged as a particular type
    """
    for node in parse_tree.iterator():
        if not node.isLeaf() and node.value() == node_type:
            yield node

def get_node_string(nodes):
    if isinstance(nodes, collections.Iterable):
        phrase = []
        for node in nodes:
            phrase.append(node.toString())
        return ' '.join(phrase)
    else:
        node = nodes
        return node.toString()
    

def extract_subject_nodes(tokenized_string, lexical_parser=lexical_parser):
    """
    returns words which are marked as subjects
    
    >>> import nltk
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> raw_input_string = "I like ripe bannanas."
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> subject_nodes = extract_subject_nodes(tokenized_string)
    >>> print get_node_string(subject_nodes)
    bannanas
    >>> raw_input_string = "I like Japanese food."
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> subject_nodes = extract_subject_nodes(tokenized_string)
    >>> print get_node_string(subject_nodes)
    Japanese food
    """
    tree = get_parse_tree(tokenized_string)
    # find subject node
    subjectNodes = get_nodes_by_type(tree, 'S')
    # find the reffering noun
    for subjectNode in subjectNodes:
        nnsNodes = get_nodes_by_type(subjectNode, 'NNS')
        if nnsNodes:
            # return the noun node
            for nnsNode in nnsNodes:
                return nnsNode.firstChild().iterator()
        vpNodes = get_nodes_by_type(subjectNode, 'VP')
        for vpNode in vpNodes:
            npNodes = get_nodes_by_type(vpNode, 'NP')
            if npNodes:
                for npNode in npNodes:
                    return npNode.getLeaves().iterator()
        return []
                
def extract_sentence_type(tokenized_string, lexical_parser=lexical_parser):
    """
    >>> import nltk
    >>> raw_input_string = "What can I make with carrots?"
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> print extract_sentence_type(tokenized_string)
    ('question', u'What')
    """
    question_grammar = ['WRB', 'WP'] #['WHADVP', 'WHNP']
    
    tree = get_parse_tree(tokenized_string)
    for qg in question_grammar:
        question_nodes = get_nodes_by_type(tree, qg)
        question_node = _iterator_first(question_nodes)
        if question_node: # sentence is a question
            return ('question', question_node.getLeaves()[0].value())
    return (None,None)
    
def extract_word_modifiers(tokenized_string):
    pass
