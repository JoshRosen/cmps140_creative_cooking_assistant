from collections import defaultdict
from wordlists import list_of_adjectivals
from nlu.recipes import normalize_ingredient_name
from ingredient_cuisine_mapping import ingredient_cuisine_mapping


def get_cuisine(words, ingredient_weight=1, adjectival_weight=3):
    """
    Given an array of words, return a dictionary whose keys are cuisines
    associated with this recipe and whose values are scores representing
    relative strengths of the cuisine associations.

    The relative weights of ingredients and nationality adjectives can be
    adjusted through the *_weight keyword arguments.

    >>> get_cuisine(["Apple Pie Spice", "Prosciutto", "black pepper"])
    defaultdict(<type 'int'>, {'Indonesian': 1, 'Sausage': 1, 'Italian': 1})

    >>> get_cuisine(["Apple Pie Spice", "Prosciutto", "black pepper",
    ...              "Italian"])
    defaultdict(<type 'int'>, {'Indonesian': 1, 'Sausage': 1, 'Italian': 4})

    >>> get_cuisine(["Apple", "Prosciutto", "Pasta", "Stuffed Chicken Breast",
    ...              "Israeli", "American"])
    defaultdict(<type 'int'>, {'Israeli': 3, 'American': 3, 'Italian': 2})
    """
    cuisines = defaultdict(int)  # Maps cuisine to frequency of occurrence
    for word in words:
        #Check for nationality adjectives like "American" or "Japanese"
        if word in list_of_adjectivals:
            cuisines[word] += adjectival_weight
        # Check for cuisines strongly associated with certain ingredients
        normal = normalize_ingredient_name(word)
        if normal in ingredient_cuisine_mapping:
            for cuisine in ingredient_cuisine_mapping[normal]:
                cuisines[cuisine] += ingredient_weight
    return cuisines
