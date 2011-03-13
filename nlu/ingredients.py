"""
Parsing for ingredient lines of recipes.
"""
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import wordlists
from ingredient_line_grammar import ingredient_line
import pyparsing


LEMMATIZER = WordNetLemmatizer()


def is_ingredient(word):
    """
    Return True if the word is an ingredient, False otherwise.

    >>> is_ingredient('milk')
    True
    >>> is_ingredient('blackberries')
    True
    >>> is_ingredient('Canada')
    False
    >>> is_ingredient('breakfast')
    False
    >>> is_ingredient('dish')
    False
    """
    reject_synsets = ['meal.n.01', 'meal.n.02', 'dish.n.02', 'vitamin.n.01']
    reject_synsets = set(wordnet.synset(w) for w in reject_synsets)
    accept_synsets = ['food.n.01', 'food.n.02']
    accept_synsets = set(wordnet.synset(w) for w in accept_synsets)
    for word_synset in wordnet.synsets(word, wordnet.NOUN):
        all_synsets = set(word_synset.closure(lambda s: s.hypernyms()))
        all_synsets.add(word_synset)
        for synset in reject_synsets:
            if synset in all_synsets:
                return False
        for synset in accept_synsets:
            if synset in all_synsets:
                return True
    return word in wordlists.ingredients


def normalize_ingredient_name(ingredient_name):
    """
    Normalizes an ingredient name, removing pluralization.
    >>> normalize_ingredient_name('eggs')
    'egg'
    >>> normalize_ingredient_name('bing cherries')
    'bing cherry'
    """
    words = ingredient_name.lower().strip().split()
    return ' '.join(LEMMATIZER.lemmatize(w) for w in words)


def extract_ingredient_parts(ingredient_string):
    """
    Extracts the unit, quantity, base ingredient, and modifiers from an item in
    a recipe's ingredient list.  Returns a dictionary, or None if nothing could
    be parsed.

    Simple examples:

    >>> extract_ingredient_parts('12 cups lettuce')
    {'base_ingredient': 'lettuce', 'unit': 'cups', 'quantity': '12'}
    >>> extract_ingredient_parts("14 large, fresh eggs")
    {'base_ingredient': 'egg', 'modifiers': 'large, fresh', 'quantity': '14'}

    More complex quantities:

    >>> extract_ingredient_parts('1 1/2 tbsp olive oil')
    {'base_ingredient': 'olive oil', 'unit': 'tbsp', 'quantity': '1 1/2'}
    >>> extract_ingredient_parts('1 (12 ounce) package tofu')
    {'base_ingredient': 'tofu', 'unit': '(12 ounce) package', 'quantity': '1'}

    Modifiers that appear after ingredients:

    >>> extract_ingredient_parts('apple, cored, peeled')
    {'base_ingredient': 'apple', 'modifiers': 'cored, peeled'}

    TODO: handle separators like ' - ' and parentheses.

    Invalid ingredient strings:

    >>> extract_ingredient_parts('1 1/2') == None
    True
    """
    try:
        parsed = ingredient_line.parseString(ingredient_string)
    except pyparsing.ParseException:
        return None
    parts = {}
    if 'quantity' in parsed:
        parts['quantity'] = parsed['quantity'].strip()
    if 'unit' in parsed:
        parts['unit'] = parsed['unit'].strip()
    parts['base_ingredient'] = \
        normalize_ingredient_name(parsed['base_ingredient'])
    if 'pre_modifiers' in parsed or 'post_modifiers' in parsed:
        parts['modifiers'] = ''
        if 'pre_modifiers' in parsed:
            parts['modifiers'] = parsed['pre_modifiers'].strip()
        if 'post_modifiers' in parsed:
            if 'pre_modifiers' in parsed:
                parts['modifiers'] += ', ' + parsed['post_modifiers'].strip()
            else:
                parts['modifiers'] = parsed['post_modifiers'].strip()
    return parts
