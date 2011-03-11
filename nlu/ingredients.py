"""
Parsing for ingredient lines of recipes.
"""
import re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import wordlists
from wordlists import units_of_measure, food_adjectives


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


def is_unit_of_measurement(word):
    """
    >>> is_unit_of_measurement('ounces')
    True
    """
    return LEMMATIZER.lemmatize(word) in units_of_measure


def is_food_adjective(word):
    """
    >>> is_food_adjective("chopped")
    True
    """
    return LEMMATIZER.lemmatize(word) in food_adjectives


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


def tokenize_group_parens(input_string):
    """
    Tokenize the input string while treating text in parentheses as a single
    token.

    >>> tokenize_group_parens("1 (12 ounce) package")
    ['1', '(12 ounce)', 'package']
    """
    regexp = r"\([^)]+\)|[a-zA-Z0-9_,.-]+"
    return re.findall(regexp, input_string)


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
    parts = {}
    ingredient_string = ingredient_string.strip()
    tokens = []

    # Handle units and quantities, if they are present:
    # Extract the quantity using a regular expression (to handle '1 1/2')
    match = re.match(r"^([0-9/ -]+)(.*)$", ingredient_string)
    if match:
        parts['quantity'] = match.group(1).strip()
        tokens = tokenize_group_parens(match.group(2))
        # Extract unit of measurement.  In cases like '1 (12 ounce) package',
        # '(12 ounce) package' is the unit of measurement.
        # TODO: Perhaps the unit of measurement should be normalized.
        unit_tokens = []
        while tokens and (is_unit_of_measurement(tokens[0]) or \
            tokens[0].startswith('(')):
            unit_tokens.append(tokens.pop(0))
        if unit_tokens:
            parts['unit'] = ' '.join(unit_tokens)
    else:
        tokens = tokenize_group_parens(ingredient_string)

    # Hopefully, the remaining tokens describe the ingredient.  There may be
    # modifiers, like 'grated cheese'.  To extract the base ingredient, use
    # WordNet.
    modifier_tokens = []
    while tokens and is_food_adjective(tokens[0].strip(',')):
        modifier_tokens.append(tokens.pop(0))
    remainder = ' '.join(tokens)
    # If we've gotten this far and run out of tokens, then the ingredient
    # string is not well-formed.
    if not remainder:
        return None
    # To deal with modifiers that appear AFTER the base ingredient, assume that
    # they are preceded by a comma.
    if ',' not in remainder:
        # No modifiers after base ingredient
        parts['base_ingredient'] = normalize_ingredient_name(remainder)
        parts['modifiers'] = ' '.join(modifier_tokens)
    else:
        # Modifiers after base ingredient
        (base_ingredient, post_modifiers) = remainder.split(',', 1)
        post_modifiers = post_modifiers.strip()
        if post_modifiers and not modifier_tokens:
            parts['modifiers'] = post_modifiers
        else:
            # If we have modifiers before and after the ingredient, separate
            # them with a comma.
            parts['modifiers'] = ', '.join([' '.join(modifier_tokens),
                post_modifiers])
        parts['base_ingredient'] = normalize_ingredient_name(base_ingredient)
    if not parts['modifiers']:
        del parts['modifiers']
    return parts
