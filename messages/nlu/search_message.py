from data_structures import ParsedInputMessage
import random
import nltk
from nltk.corpus import wordnet

def stem_words(words, stemmer=nltk.LancasterStemmer()):
    return [stemmer.stem(word) for word in words]
      
def discoverHypernyms(word):
    for synset in wordnet.synsets(word):
        print synset, synset.hypernyms()

class SearchMessage(ParsedInputMessage):
    # attributes in the frame
    #frame_keys = ['ingredientients', 'cost', 'callories', 'time_total', 'time_prep',
    #        'time_cook', 'culture', 'actions', 'instruments', 'food_type',
    #        'author', 'meal_time', 'course', 'taste', 'food_group']
    frame_keys = ['meal', 'dish', 'ingredient']
    keywords = ['desire.v.01', 'like.v.05', 'need.n.02', 'looking.n.02',
                'search.v.02', 'want.v.03', 'want.v.04']
    
    
    def parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        super(SearchMessage, self).parse(raw_input_string)
        
        
    @staticmethod
    def confidence(raw_input_string):
        minDistance = 3
        bestDistance = float('inf')
        
        # Find the best keyword synset distance to input string
        for keyword in SearchMessage.keywords:
            keywordSyn = wordnet.synset(keyword)
            for word in raw_input_string.split(' '):
                for wordSyn in wordnet.synsets(word):
                    distance = keywordSyn.shortest_path_distance(wordSyn)
                    if distance != None:
                        bestDistance = min(bestDistance, distance)
                    
        print "best: ", bestDistance
        if bestDistance <= minDistance:
            return (1-(float(bestDistance)/minDistance)) * .5 + .5
        else:
            return 0.0
