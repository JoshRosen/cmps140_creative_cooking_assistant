from collections import defaultdict
from wordlists import list_of_adjectivals
from nlu import normalize_ingredient_name
from ingredient_cuisine_mapping import ingredient_cuisine_mapping


def get_cuisine(title, description, ingredients, title_weight=10,
                description_weight=5, ingredient_weight=1):
    """
    Given a title (string), a description (string), and a list of 
    ingredients (list of strings), it will return a most likely cuisine
    that is what the given data is. The value attached to the cuisine 
    that is highest is the most probable cuisine. 

    The relative weights of the hits from the title, description, and 
    ingredients are modifiable via arguments 4, 5, and 6 (respectively)

    >>> get_cuisine("Japanese Pork Fried Rice","My Japanese grandmother 
    ...     gave me this recipe",["Pork","rice","vinegar","cabbage"])
    defaultdict(<type 'int'>, {'Sausage': 1, 'Japanese': 15})

    >>> get_cuisine("Thai Chicken","This recipe was created when we 
    ... felt like having spicy, Oriental tasting food. It's delicious, 
    ... and uses bold ingredients such as peanut butter, fresh ginger 
    ... and sesame oil. Try serving over rice.",["soy sauce", "garlic", 
    ... "ginger", "chicken", "sesame oil", "peanut butter", "green 
    ... onions"])
    defaultdict(<type 'int'>, {'Thai': 10, 'Indonesian': 1, 'Sausage': 1})

    >>> get_cuisine("Italian Rice Balls","Crispy meatball-sized 
    ... appetizers with deep fried outsides and moist herb and cheese 
    ... insides",["water","brown rice","garlic","bay leaf","prosciutto",
    ... "basil","olive oil","egg whites","Parmesan","bread crumbs",
    ... "vegetable oil"])
    defaultdict(<type 'int'>, {'Pizza': 2, 'Italian': 11})

    """
    cuisines = defaultdict(int)  # Maps cuisine to frequency of occurrence
    title_words = title.split() #split the words into an iterable list
    for word in title_words:    #iterate through the title
        if word in list_of_adjectivals:
            cuisines[word] += title_weight #add the weight

    description_words = description.split() #split up the description 
    for word in description_words:  #iterate through the description
        if word in list_of_adjectivals:
            cuisines[word] += description_weight    #add the weight

    for word in ingredients:    #go through the ingredients list
        # Check for cuisines strongly associated with certain ingredients
        normal = normalize_ingredient_name(word)
        if normal in ingredient_cuisine_mapping:
            for cuisine in ingredient_cuisine_mapping[normal]:
                cuisines[cuisine] += ingredient_weight
    return cuisines
