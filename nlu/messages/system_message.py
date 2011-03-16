import nltk
from nltk.corpus import wordnet

from nlu.messages.parsed_input_message import ParsedInputMessage
from nlu.messages.msgutils import extract_close_keywords
from nlu.messages.msgutils import get_keyword_confidence
import utils

class SystemMessage(ParsedInputMessage):
    frame_keys = ['action']
    exit_keywords = ['adieu.n.01', 'bye.n.01', 'farewell.n.02', 'exit.v.01']
    restart_keywords = ['restart.v.01', 'reload.v.02']
    keywords = exit_keywords + restart_keywords
                
    def _parse(self, raw_input_string, generators):
        """
        Fills out message meta and frame attributes
        """
        tokenized_string = g.generate_tokenized_string(raw_input_string)

        wordActionMap = {'exit':SystemMessage.exit_keywords, 'restart':SystemMessage.restart_keywords}
        for action, keywords in wordActionMap.items():
            matches = extract_close_keywords(keywords, tokenized_string, 3)
            if matches: # synset of keyword was found in the sentence
                self.frame['action'] = action
         
    @staticmethod
    def confidence(raw_input_string, generators):
        return get_keyword_confidence(raw_input_string,
                                      SystemMessage.keywords,
                                      3)
 
    def __repr__(self):
        return '<%s: frame:%s>' % (self.__class__.__name__, self.frame)

