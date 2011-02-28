import nltk
from nltk.corpus import wordnet

from data_structures import ParsedInputMessage
import utils

class YesNoMessage(ParsedInputMessage):
    """
    >>> YesNoMessage.confidence("Hmmm... No thanks.")
    1.0
    >>> ynm = YesNoMessage("Hmmm... No thanks.")
    >>> ynm.frame['decision']
    {'decision': 'no', 'word': 'No', 'id': 2}
    >>> YesNoMessage.confidence("Ok")
    1.0
    >>> ynm = YesNoMessage("Ok")
    >>> ynm.frame['decision']
    {'decision': 'yes', 'word': 'Ok', 'id': 0}
    >>> YesNoMessage.confidence("Sounds good")
    1.0
    >>> ynm = YesNoMessage("Sounds good")
    >>> ynm.frame['decision']
    {'decision': 'yes', 'word': 'good', 'id': 1}
    >>> YesNoMessage.confidence("I like turtles?")
    0.0
    >>> ynm = YesNoMessage("I like turtles?")
    >>> ynm.frame['decision'] == None
    True
    """

    frame_keys = ['decision']
    yes_keywords = ['yes.n.01','okay.r.01', 'alright.s.01', 'very_well.r.02',
                    'good.n.03']
    no_keywords = ['no.n.01' ]
    minDistance = 3
        
    
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
            self.frame['decision'] = {'id': yesIndex,
                                      'word': yesToken,
                                      'decision': 'yes',
                                     }
        elif noDistanceSet and yesDistanceSet == None:
            self.frame['decision'] = {'id': noIndex,
                                      'word': noToken,
                                      'decision': 'no',
                                     }
        else: # conflict
            self.frame['decision'] = None
            
            
        
    @staticmethod
    def confidence(raw_input_string):
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        
        yesDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.yes_keywords,
                            tokenized_string)
        noDistanceSet = utils.min_synset_distance_in_sentence(
                            YesNoMessage.no_keywords,
                            tokenized_string)
                            
        # check minDistance
        if yesDistanceSet and yesDistanceSet[1] <= YesNoMessage.minDistance:
            return 1.0
        else:
            yesDistanceSet = None
        if noDistanceSet and noDistanceSet[1] <= YesNoMessage.minDistance:
            return 1.0
        else:
            noDistanceSet = None
        if yesDistanceSet == None and noDistanceSet == None:
            return 0.0
            
