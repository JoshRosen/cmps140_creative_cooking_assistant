"""
Recognize recipe search utterances.
"""
import nltk
from nltk.corpus import wordnet
import utils
import wordlists


def get_ingredients(tokenized_string, enum=True):
    """
    Returns a tuple of (index, ingredient) or a list of ingredients from a
    tokenized string.

    >>> raw_input_string = "I like apples, cinnamon, and pepper."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_ingredients(tokenized_string): print i,w
    2 apples
    4 cinnamon
    7 pepper
    """

    stemmed_string = utils.stem_words(tokenized_string)
    stemmed_ingredients = utils.stem_words(wordlists.ingredients)
    results = _extract_words_from_list(stemmed_ingredients,
                                       stemmed_string,
                                       enum)
    return [(i, tokenized_string[i]) for (i, _) in results]


def get_meals(tokenized_string, enum=True):
    """
    Returns a tuple of (index, meal) or a list of meals from a
    tokenized string.

    >>> raw_input_string = "I want cats for breakfast and dogs for dinner."
    >>> tokenizer = nltk.WordPunctTokenizer()
    >>> tokenized_string = tokenizer.tokenize(raw_input_string)
    >>> for i,w in get_meals(tokenized_string): print i,w
    4 breakfast
    8 dinner
    """

    stemmed_string = utils.stem_words(tokenized_string)
    stemmed_meals = utils.stem_words(wordlists.meal_types)
    results = _extract_words_from_list(stemmed_meals, stemmed_string, enum)
    return [(i, tokenized_string[i]) for (i, _) in results]


def get_cuisines(tokenized_string, enum=True):
    """
    Returns a tuple of (index, cuisine) or a list of cuisines from a
    tokenized string.

    #>>> raw_input_string = "I want a chinese or mexican dish."
    #>>> tokenizer = nltk.WordPunctTokenizer()
    #>>> tokenized_string = tokenizer.tokenize(raw_input_string)
    #>>> for i,w in get_cuisines(tokenized_string): print i,w
    #TODO: Implement doctest
    """

    stemmed_string = utils.stem_words(tokenized_string)
    cuisines = set.difference(wordlists.cuisines, wordlists.meal_types)
    stemmed_cuisines = utils.stem_words(cuisines)
    results = _extract_words_from_list(stemmed_cuisines, stemmed_string, enum)
    return [(i, tokenized_string[i]) for (i, _) in results]


def _extract_words_from_list(word_list, string_list, enum=True):
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


def recipe_search_message(nlu, raw_input_string):
    """
    Recognizes searches for recipes.  The frame may contain the following keys:

    frame_keys = ['ingredientients', 'cost', 'callories', 'time_total',
        'time_prep', 'time_cook', 'culture', 'actions', 'instruments',
        'food_type', 'author', 'meal_time', 'course', 'taste', 'food_group']

    Currently, only ['ingredient', 'meal', 'cuisine'] is supported.

    >>> recipe_search_message(None, "I would like breakfast recipes.")
    {'confidence': 1.0, 'msg_type': 'recipe_search', 'meals': ['breakfast']}
    >>> recipe_search_message(None, "This is completely off-topic.") == None
    True
    """
    result = {
        'msg_type': 'recipe_search',
        'confidence': _recipe_search_message_confidence(raw_input_string),
        'raw_input_string': raw_input_string,
        'ingredients': [],
        'meals': [],
        'cuisines': [],
        'dishes': [],
    }

    tokenizer = nltk.WordPunctTokenizer()
    tokenized_string = tokenizer.tokenize(raw_input_string)

    # Ingredients
    for (i, _) in get_ingredients(tokenized_string):
        ingredient = tokenized_string[i]
        result['ingredients'].append(ingredient)

    # Meals
    for (i, _) in get_meals(tokenized_string):
        meal = tokenized_string[i]
        result['meals'].append(meal)

    # Cuisines
    for (i, _) in get_cuisines(tokenized_string):
        cuisine = tokenized_string[i]
        result['cuisines'].append(cuisine)

    # Dishes
    # TODO: Get the subject of the sentence (aka what the verb is reffering to)
    #dishes_set = [(i, w[0]) for (i, w) in enumerate(tagged_string) if
                          #w[1]=='NN' and
                          #w[0] not in result['ingredients'] and
                          #w[0] not in result['meals']]
    #for (i, _) in dishes_set:
        #dish = tokenized_string[i]
        #result['dishes'].append(dish)

    result = utils.dict_remove_empty(result)
    standard_fields = set(['msg_type', 'confidence', 'raw_input_string'])
    if set(result.keys()) - standard_fields:
        return result
    else:
        return None


def _recipe_search_message_confidence(raw_input_string):
    """
    Determine confidence for recipe_search_message.
    """
    keywords = ['desire.v.01', 'like.v.05', 'need.n.02', 'looking.n.02',
                'search.v.02', 'want.v.03', 'want.v.04', 'create.v.05']

    # TODO: configure minDistance on a per-keyword basis
    min_distance = 3
    best_distance = float('inf')

    # Find the best keyword synset distance to input string
    for keyword in keywords:
        keyword_syn = wordnet.synset(keyword)
        for word in raw_input_string.split():
            for word_syn in wordnet.synsets(word):
                distance = keyword_syn.shortest_path_distance(word_syn)
                if distance != None:
                    best_distance = min(best_distance, distance)

    if best_distance <= min_distance:
        # TODO: determine best metric for this
        # return 1.0/temperature^**bestDistance
        return (1 - (float(best_distance) / min_distance)) * .5 + .5
    else:
        return 0.0
