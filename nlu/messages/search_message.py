from nlu.messages.parsed_input_message import ParsedInputMessage
import nltk
from nltk.corpus import wordnet
import utils
import wordlists

from nlu import is_ingredient, normalize_ingredient_name


def get_ingredients(tokenized_string, enum=False):
    """
    Returns a tuple of (index, ingredient) or a list of ingredients from a
    tokenized string.

    >>> raw_input_string = "I like apples, cinnamon, and pepper."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_ingredients(tokenized_string, enum=True): print i,w
    2 apples
    4 cinnamon
    7 pepper
    """
    words = [normalize_ingredient_name(x) for x in tokenized_string]
    results = [x for x in enumerate(words) if is_ingredient(x[1])]
    if enum:
        return [(i, tokenized_string[i]) for i, w in results]
    else:
        return [tokenized_string[i] for i, w in results]


def get_meals(tokenized_string, enum=False):
    """
    Returns a tuple of (index, meal) or a list of meals from a
    tokenized string.
    
    >>> raw_input_string = "I want cats for breakfast and dogs for dinner."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_meals(tokenized_string, enum=True): print i,w
    4 breakfast
    8 dinner
    """
    
    stemmed_string = utils.stem_words(tokenized_string)
    stemmed_meals = utils.stem_words(wordlists.meal_types)
    results = _extract_words_from_list(stemmed_meals, stemmed_string, True)
    if enum:
        return [(i, tokenized_string[i]) for i, w in results]
    else:
        return [tokenized_string[i] for i, w in results]
    
def get_cuisines(tokenized_string, enum=False):
    """
    Returns a tuple of (index, cuisine) or a list of cuisines from a
    tokenized string.
    
    >>> raw_input_string = "I want a chinese or mexican dish."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_cuisines(tokenized_string, enum=True): print i,w
    3 chinese
    5 mexican
    """
    
    stemmed_string = utils.stem_words(tokenized_string)
    cuisines = set.difference(wordlists.cuisines, wordlists.meal_types)
    cuisines = cuisines.union(wordlists.list_of_adjectivals)
    stemmed_cuisines = utils.stem_words(cuisines)
    results = _extract_words_from_list(stemmed_cuisines, stemmed_string, True)
    if enum:
        return [(i, tokenized_string[i]) for i, w in results]
    else:
        return [tokenized_string[i] for i, w in results]

def _extract_words_from_list(word_list, string_list, enum=False):
    """
    Returns (index, word) or a list of words for words which occur in both
    lists.
    """
    
    for i, word in enumerate(string_list):
        if word in word_list:
            if enum:
                yield (i, word)
            else:
                yield word

class SearchMessage(ParsedInputMessage):
    """
    >>> # Test Confidence
    >>> SearchMessage.confidence('I like apples and carrots.')
    1.0
    >>> SearchMessage.confidence('I am looking for a breakfast dish.')
    1.0
    >>> SearchMessage.confidence('What can I make with bricks?')
    1.0
    
    >>> # Test _parse
    >>> sm = SearchMessage('I like apples and carrots.')
    >>> for ingredient in sm.frame['ingredient']: print ingredient['name']
    apples
    carrots
    >>> sm.frame['meal']
    []
    >>> sm.frame['cuisine']
    []
    >>> sm = SearchMessage('I am looking for a breakfast dish.')
    >>> for meal in sm.frame['meal']: print meal['name']
    breakfast
    >>> sm.frame['ingredient']
    []
    >>> sm.frame['cuisine']
    []
    >>> sm = SearchMessage('What are some turkish breakfast recipes?')
    >>> for cuisine in sm.frame['cuisine']: print cuisine['name']
    turkish
    >>> for meal in sm.frame['meal']: print meal['name']
    breakfast
    >>> sm.frame['ingredient']
    []
    """
    # attributes in the frame
    #frame_keys = ['ingredientients', 'cost', 'callories', 'time_total', 'time_prep',
    #        'time_cook', 'culture', 'actions', 'instruments', 'food_type',
    #        'author', 'meal_time', 'course', 'taste', 'food_group']
    frame_keys = ['ingredient', 'dish', 'meal', 'cuisine']
    keywords = ['desire.v.01', 'like.v.05', 'need.n.02', 'looking.n.02',
                'search.v.02', 'want.v.03', 'want.v.04', 'create.v.05']
    
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes.
        """
        tokenizer = nltk.WordPunctTokenizer()
        tokenized_string = tokenizer.tokenize(raw_input_string)
        tagger = utils.combined_taggers
        tagged_string = tagger.tag(tokenized_string)
        
        # Ingredients
        for i, ingredient in get_ingredients(tokenized_string, enum=True):
            self.frame['ingredient'].append({'id': i,
                                             'name': ingredient,
                                             'descriptor': [], # TODO: siblings JJ
                                             'preference': 0, # TODO: RB = not or n't
                                             'relationship': 'and', #TODO: Implement
                                             })
        # Meals
        for i, meal in get_meals(tokenized_string, enum=True):
            meal = tokenized_string[i]
            self.frame['meal'].append({'id': i,
                                       'name': meal,
                                       'descriptor': [], # TODO: siblings JJ
                                       'preference': 0, # TODO: RB = not or n't
                                       'relationship': 'and', #TODO: Implement
                                       })
        # Cuisine
        for i, cuisine in get_cuisines(tokenized_string, enum=True):
            self.frame['cuisine'].append({'id': i,
                                          'name': cuisine,
                                          'descriptor': [], # TODO: siblings JJ
                                          'preference': 0, # TODO: RB = not or n't
                                          'relationship': 'and', #TODO: Implement
                                         })
        # Dish
        # TODO: Get the subject of the sentence (aka what the verb is reffering to)
        
        dishesSet = [(i, w[0]) for i,w in enumerate(tagged_string) if w[1]=='NN' and
                              w[0] not in self.frame['ingredient'] and
                              w[0] not in self.frame['meal']]
        for i, dish in dishesSet:
            self.frame['dish'].append({'id': i,
                                       'name': dish,
                                       'descriptor': [], # TODO: siblings JJ
                                       'preference': 0, # TODO: RB = not or n't
                                       'relationship': 'and', #TODO: Implement
                                       })
        
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
