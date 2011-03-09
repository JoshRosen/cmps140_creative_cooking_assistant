from nlu.messages.parsed_input_message import ParsedInputMessage
from nlu.stanford_utils import extract_subject_nodes
from nlu.stanford_utils import get_node_string
from nlu.stanford_utils import _iterator_first


import nltk
from nltk.corpus import wordnet

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

class PreferenceMessage(ParsedInputMessage):
    """
    >>> pm = PreferenceMessage('I like Japanese food.')
    >>> print pm.frame
    {'word': 'like', 'temporal': 'permanent', 'prefer': True, 'subject': [u'Japanese', u'food']}
    >>> pm = PreferenceMessage('I like carrots.')
    >>> print pm.frame
    {'word': 'like', 'temporal': 'permanent', 'prefer': True, 'subject': [u'carrots']}
    >>> pm = PreferenceMessage('I want carrots.')
    >>> print pm.frame
    {'word': 'want', 'temporal': 'temporary', 'prefer': True, 'subject': [u'carrots']}
    """
    frame_keys = ['prefer', 'word', 'subject', 'temporal']
    keywords_temporary_pos = ['want.v.03', 'want.v.04', 'want.v.05']
    keywords_temporary_neg = []
    keywords_permanent_pos = ['like.v.05', 'wish.v.02', 'like.v.02']
    keywords_permanent_neg = []
    keywords_temporary = keywords_temporary_pos + keywords_temporary_neg
    keywords_permanent = keywords_permanent_pos + keywords_permanent_neg
    keywords = keywords_temporary + keywords_permanent
    
    @staticmethod
    def confidence(raw_input_string):
        minDistance = 3
        bestDistance = float('inf')
        
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        
        # Find the best keyword synset distance to input string
        for keyword in PreferenceMessage.keywords:
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
        
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes.
        """
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        
        subjects = extract_subject_nodes(tokenized_string)
        if subjects:
            self.frame['subject'] = [get_node_string(subject)
                                     for subject in subjects]
        words_temporary_pos = extract_close_keywords(
                                       PreferenceMessage.keywords_temporary_pos,
                                       tokenized_string,
                                       2)
        words_temporary_neg = extract_close_keywords(
                                       PreferenceMessage.keywords_temporary_neg,
                                       tokenized_string,
                                       2)
        words_permanent_pos = extract_close_keywords(
                                       PreferenceMessage.keywords_permanent_pos,
                                       tokenized_string,
                                       2)
        words_permanent_neg = extract_close_keywords(
                                       PreferenceMessage.keywords_permanent_neg,
                                       tokenized_string,
                                       2)
        words_temporary = words_temporary_pos + words_temporary_neg
        words_permanent = words_permanent_pos + words_permanent_neg
        if words_temporary and words_permanent:
            # Confused
            # self.frame['temporal'] = None
            # self.frame['word'] = None
            # This check is skipped due to an error in not using the POS
            # when looking up synsets.
            # TODO: Fix (example: fish)
            pass
        if words_temporary:
            self.frame['temporal'] = 'temporary'
            self.frame['word'] = words_temporary[0]
        else: # words_permanent
            self.frame['temporal'] = 'permanent'
            self.frame['word'] = words_permanent[0]
        
        words_pos = words_temporary_pos + words_permanent_pos
        words_neg = words_temporary_neg + words_permanent_neg
        if words_pos and words_neg:
            # Confused
            self.frame['prefer'] = None
        if words_pos:
            self.frame['prefer'] = True
        else: # words_neg
            self.frame['prefer'] = False
