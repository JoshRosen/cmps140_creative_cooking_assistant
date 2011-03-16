from nlu.messages.parsed_input_message import ParsedInputMessage
from nlu.stanford_utils import extract_subject_nodes
from nlu.stanford_utils import get_node_string
from nlu.stanford_utils import get_parse_tree
from nlu.messages.msgutils import get_keyword_confidence
from nlu.messages.msgutils import extract_close_keywords


import nltk
from nltk.corpus import wordnet

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
        return get_keyword_confidence(raw_input_string,
                                      PreferenceMessage.keywords,
                                      3)
        
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes.
        """
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        parseTree = get_parse_tree(tokenized_string)
        
        subjects = extract_subject_nodes(parseTree)
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
