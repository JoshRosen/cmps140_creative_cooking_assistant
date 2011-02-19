from data_structures import ParsedInputMessage
import random
import nltk
from nltk.corpus import wordnet
import utils
import wordlists

class SearchMessage(ParsedInputMessage):
    # attributes in the frame
    #frame_keys = ['ingredientients', 'cost', 'callories', 'time_total', 'time_prep',
    #        'time_cook', 'culture', 'actions', 'instruments', 'food_type',
    #        'author', 'meal_time', 'course', 'taste', 'food_group']
    frame_keys = ['meal', 'dish', 'ingredient']
    keywords = ['desire.v.01', 'like.v.05', 'need.n.02', 'looking.n.02',
                'search.v.02', 'want.v.03', 'want.v.04']
    _meal_types = wordlists.meal_types
    _ingredients = wordlists.ingredients
    
    
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        super(SearchMessage, self)._parse(raw_input_string)
        
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        tagger = utils.combined_taggers
        tagged_string = tagger.tag(tokenized_string)
        
        # Meal
        meal = [w for w in self._meal_types if w in tokenized_string]
        if meal:
            self.frame['meal'] = meal
        # Ingredient
        ingredient = [w for w in self._ingredients if w in tokenized_string]
        if ingredient:
            self.frame['ingredient'] = ingredient
        # Dish
        self.frame['dish'] = [w[0] for w in tagged_string if w[1]=='NN' and
                              w[0] not in self.frame['ingredient'] and
                              w[0] not in self.frame['meal']]
        
        
        
    @staticmethod
    def confidence(raw_input_string):
        # TODO: configure minDistance on a per-keyword basis
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
                    
        if bestDistance <= minDistance:
            # TODO: determine best metric for this
            # return 1.0/temperature^**bestDistance
            return (1-(float(bestDistance)/minDistance)) * .5 + .5
        else:
            return 0.0
            
    def __repr__(self):
        return '<%s: frame:%s>' % (self.__class__.__name__, self.frame)
