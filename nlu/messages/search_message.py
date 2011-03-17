from __future__ import absolute_import
from nlu.messages.parsed_input_message import ParsedInputMessage
import nltk
from nltk.corpus import wordnet

import wordlists
import utils
from nlu import is_ingredient, normalize_ingredient_name
from nlu.stanford_utils import get_node_string
from nlu.stanford_utils import get_parse_tree
from nlu.messages.msgutils import extract_words_from_list
from nlu.messages.msgutils import extract_junction
from nlu.messages.msgutils import extract_subjects
from nlu.messages.msgutils import is_negated

def get_preference_range(parseTree, word):
    if is_negated(parseTree, word):
        return -1
    else:
        return 1
        

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
    results = extract_words_from_list(stemmed_meals, stemmed_string, True)
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
    results = extract_words_from_list(stemmed_cuisines, stemmed_string, True)
    if enum:
        return [(i, tokenized_string[i]) for i, w in results]
    else:
        return [tokenized_string[i] for i, w in results]


class SearchMessage(ParsedInputMessage):
    """
    >>> from nlu.generators import *
    >>> cache_size = 16
    >>> generators = Generators()
    >>> generators.add(Generate_Tokenized_String, cache_size)
    >>> generators.add(Generate_Stanford_Parse_Tree, cache_size)
    
    >>> # Test Confidence
    >>> SearchMessage.confidence('I like apples and carrots.', generators)
    1.0
    >>> SearchMessage.confidence('I am looking for a breakfast dish.', generators)
    1.0
    >>> SearchMessage.confidence('What can I make with bricks?', generators)
    1.0
    
    >>> # Test _parse
    >>> sm = SearchMessage('I like apples or carrots.', generators)
    >>> sm.frame['ingredient']
    [{'descriptor': [], 'relationship': 'or', 'id': 2, 'preference': 1, 'name': 'apples'}, {'descriptor': [], 'relationship': 'or', 'id': 4, 'preference': 1, 'name': 'carrots'}]
    >>> sm.frame['dish']
    []
    >>> for ingredient in sm.frame['ingredient']: print ingredient['name']
    apples
    carrots
    >>> sm.frame['meal']
    []
    >>> sm.frame['cuisine']
    []
    >>> sm = SearchMessage("I don't like apples or carrots.", generators)
    >>> sm.frame['ingredient']
    [{'descriptor': [], 'relationship': 'or', 'id': 4, 'preference': -1, 'name': 'apples'}, {'descriptor': [], 'relationship': 'or', 'id': 6, 'preference': -1, 'name': 'carrots'}]
    >>> sm = SearchMessage('I am looking for a breakfast dish.', generators)
    >>> for meal in sm.frame['meal']: print meal['name']
    breakfast
    >>> sm.frame['ingredient']
    []
    >>> sm.frame['cuisine']
    []
    >>> sm = SearchMessage('What are some turkish breakfast recipes?', generators)
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
    
    def _parse(self, raw_input_string, g):
        """
        Fills out message meta and frame attributes.
        """
        tokenized_string = g.generate_tokenized_string(raw_input_string)
        parseTree = g.generate_stanford_parse_tree(raw_input_string)
        
        # Ingredients
        for i, ingredient in get_ingredients(tokenized_string, enum=True):
            frameItem = {}
            frameItem['id'] = i
            frameItem['name'] = ingredient
            frameItem['descriptor'] = [] # TODO: siblings JJ
            frameItem['preference'] = get_preference_range(parseTree, ingredient)
            frameItem['relationship'] = extract_junction(parseTree, ingredient)
            self.frame['ingredient'].append(frameItem)
            
        # Meals
        for i, meal in get_meals(tokenized_string, enum=True):
            meal = tokenized_string[i]
            frameItem = {}
            frameItem['id'] = i
            frameItem['name'] = meal
            frameItem['descriptor'] = [] # TODO: siblings JJ
            frameItem['preference'] = extract_junction(parseTree, meal)
            frameItem['relationship'] = extract_junction(parseTree, meal)
            self.frame['meal'].append(frameItem)
            
        # Cuisine
        for i, cuisine in get_cuisines(tokenized_string, enum=True):
            frameItem = {}
            frameItem['id'] = i
            frameItem['name'] = cuisine
            frameItem['descriptor'] = [] # TODO: siblings JJ
            frameItem['preference'] = extract_junction(parseTree, cuisine)
            frameItem['relationship'] = extract_junction(parseTree, cuisine)
            self.frame['cuisine'].append(frameItem)
            
        # Dish
        dishesSet = []
        # add sentence subjects which aren't already ingredients or meals
        #TODO: Set extract_subject_nodes to hanle multiple phrases by splitting on and/or
        # write a function to parse tree into and/or sub trees
        for i, dish in extract_subjects(parseTree):
            duplicate = False
            ignoreFrames = ['cuisine', 'ingredient', 'meal']
            for frameKey in ignoreFrames:
                for item in self.frame[frameKey]:
                    if dish in item['name']: duplicate = True
            if not duplicate: dishesSet.append((i, dish))
                          
        for i, dish in dishesSet:
            frameItem = {}
            frameItem['id'] = i
            frameItem['name'] = dish
            frameItem['descriptor'] = [] # TODO: siblings JJ
            frameItem['preference'] = extract_junction(parseTree, dish)
            frameItem['relationship'] = extract_junction(parseTree, dish)
            self.frame['dish'].append(frameItem)
        
    @staticmethod
    def confidence(raw_input_string, generators):
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
