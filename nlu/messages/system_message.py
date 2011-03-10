import nltk
from nltk.corpus import wordnet

from nlu.messages.parsed_input_message import ParsedInputMessage
from nlu.messages.preference_message import extract_close_keywords
import utils

class SystemMessage(ParsedInputMessage):
    frame_keys = ['action']
    exit_keywords = ['adieu.n.01', 'bye.n.01', 'farewell.n.02', 'exit.v.01']
    restart_keywords = ['restart.v.01']
    keywords = exit_keywords + restart_keywords
                
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
       
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        tagger = utils.combined_taggers
        tagged_string = tagger.tag(tokenized_string)

        wordActionMap = {'exit':SystemMessage.exit_keywords, 'restart':SystemMessage.restart_keywords}
        for action, keywords in wordActionMap.items():
            matches = extract_close_keywords(keywords, tokenized_string, 3)
            if matches: # synset of keyword was found in the sentence
                self.frame['action'] = action
         
    @staticmethod
    def confidence(raw_input_string):
        minDistance = 3
        bestDistance = float('inf')

        # Find the best keyword synset distance to input string
        for keyword in SystemMessage.keywords:
            keywordSyn = wordnet.synset(keyword)
            for word in raw_input_string.split(' '):
                for wordSyn in wordnet.synsets(word):
                    distance = keywordSyn.shortest_path_distance(wordSyn)
                    if distance != None:
                        bestDistance = min(bestDistance, distance)

        if bestDistance <= minDistance:
            return (1-(float(bestDistance)/minDistance)) * .5 + .5
        else:
            return 0.0
 
    def __repr__(self):
        return '<%s: frame:%s>' % (self.__class__.__name__, self.frame)

