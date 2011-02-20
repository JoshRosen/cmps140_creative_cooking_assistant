from data_structures import ParsedInputMessage
import random
import nltk
from nltk.corpus import wordnet
from utils import stem_words
import wordlists

def get_ingredients(tokenized_string, enum=True):
    """
    Returns a tuple of (index, ingredient) or a list of ingredients from a
    tokenized string.
    
    >>> raw_input_string = "I like apples, cinnamon, and pepper."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_ingredients(tokenized_string): print i,w
    2 appl
    4 cinnamon
    7 pep
    """
    
    stemmed_string = stem_words(tokenized_string)
    stemmed_ingredients = stem_words(wordlists.ingredients)
    return _extract_words_from_list(stemmed_ingredients, stemmed_string, enum)
    
def get_meals(tokenized_string, enum=True):
    """
    Returns a tuple of (index, meal) or a list of meals from a
    tokenized string.
    
    >>> raw_input_string = "I want cats for breakfast and dogs for dinner."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_meals(tokenized_string): print i,w
    4 breakfast
    8 din
    """
    
    stemmed_string = stem_words(tokenized_string)
    stemmed_ingredients = stem_words(wordlists.meal_types)
    return _extract_words_from_list(stemmed_ingredients, stemmed_string, enum)

def _extract_words_from_list(word_list, string_list, enum=True):
    """
    """
    
    for i, word in enumerate(string_list):
        if word in word_list:
            if enum:
                yield (i, word)
            else:
                yield word

class GenericFrame:
    def __init__(self, name, prefference=0, descriptor=None):
        self.name = None
        self.prefference = None
        self.descriptor = None

class IngredientFrame(GenericFrame):
    pass
class MealFrame(GenericFrame):
    pass

class SearchMessage(ParsedInputMessage):
    # attributes in the frame
    #frame_keys = ['ingredientients', 'cost', 'callories', 'time_total', 'time_prep',
    #        'time_cook', 'culture', 'actions', 'instruments', 'food_type',
    #        'author', 'meal_time', 'course', 'taste', 'food_group']
    frame_keys = ['ingredient', 'dish', 'meal', 'cuisine']
    keywords = ['desire.v.01', 'like.v.05', 'need.n.02', 'looking.n.02',
                'search.v.02', 'want.v.03', 'want.v.04']
    _meal_types = wordlists.meal_types
    
    
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        tagger = utils.combined_taggers
        tagged_string = tagger.tag(tokenized_string)
        
        # Ingredients
        for i, stem_ingredient in get_ingredients(tokenized_string):
            ingredient = tokenized_string[i]
            self.frame['ingredient'].append(IngredientFrame(
                                            name = ingredient,
                                            descriptor = [], # siblings JJ
                                            prefference = 0, # RB = not or n't
                                            ))
        # Meals
        for i, stem_ingredient in get_ingredients(tokenized_string):
            meal = tokenized_string[i]
            self.frame['ingredient'].append(MealFrame(
                                            name = meal,
                                            descriptor = [], # siblings JJ
                                            prefference = 0, # RB = not or n't
                                            ))
        
        
        
        
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
