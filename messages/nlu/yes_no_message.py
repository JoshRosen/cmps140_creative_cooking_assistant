import nltk
from nltk.corpus import wordnet

from data_structures import ParsedInputMessage
import utils

class YesNoMessage(ParsedInputMessage):
    """
    >>> YesNoMessage("Hmmm... No thanks.")
    <YesNoMessage: frame:{'decision': <DecisionFrame: decision='no', id='2' ...>}>
    >>> YesNoMessage("Ok")
    <YesNoMessage: frame:{'decision': <DecisionFrame: decision='yes', id='0' ...>}>
    >>> YesNoMessage("Sounds good")
    <YesNoMessage: frame:{'decision': <DecisionFrame: decision='yes', id='1' ...>}>
    >>> YesNoMessage("I like turtles?")
    <YesNoMessage: frame:{'decision': []}>
    """

    frame_keys = ['decision']
    yes_keywords = ['yes.n.01','okay.r.01', 'alright.s.01', 'very_well.r.02',
                    'good.n.03']
    no_keywords = ['no.n.01' ]
    keywords = yes_keywords + no_keywords
    
    class DecisionFrame:
        def __init__(self, id, word, decision):
            self.id = id
            self.decision = decision
            self.word = word
        
        def __repr__(self):
            return '<%s: decision=\'%s\', id=\'%i\' ...>' % (self.__class__.__name__, self.decision, self.id)
    
    def __init__(self, raw_input_string):
        super(self)(raw_input_string)
        self.minDistance = 3
    
    def _parse(self, raw_input_string):
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        
        yesDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.yes_keywords,
                            tokenized_string)
        noDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.no_keywords,
                            tokenized_string)
                            
        # check minDistance and fill out variables
        if yesDistanceSet and yesDistanceSet[1] <= self.minDistance:
            yesSet, yesDistance = yesDistanceSet
            yesToken, yesIndex = yesSet
        else:
            yesDistanceSet = None
        if noDistanceSet and noDistanceSet[1] <= self.minDistance:
            noSet, noDistance = noDistanceSet
            noToken, noIndex = noSet
        else:
            noDistanceSet = None
        
        # check conflicts and update frame
        if yesDistanceSet and noDistanceSet == None:
            self.frame['decision'] = self.DecisionFrame(
                                        id=yesIndex,
                                        word=yesToken,
                                        decision='yes',
                                        )
        elif noDistanceSet and yesDistanceSet == None:
            self.frame['decision'] = self.DecisionFrame(
                                        id=noIndex,
                                        word=noToken,
                                        decision='no',
                                        )
        else: # conflict
            self.frame['decision'] = []
            
            
        
    @staticmethod
    def confidence(raw_input_string):
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        minDistance = 3
        
        yesDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.yes_keywords,
                            tokenized_string)
        noDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.no_keywords,
                            tokenized_string)
                            
        # check minDistance
        if yesDistanceSet and yesDistanceSet[1] <= self.minDistance:
            return 1.0
        else:
            yesDistanceSet = None
        if noDistanceSet and noDistanceSet[1] <= self.minDistance:
            return 1.0
        else:
            noDistanceSet = None
        if yesDistance == None and noDistance == None:
            return 0.0
            
