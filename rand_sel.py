import time
import string
import re
import sys
import os
import random
import bisect
from types import *

def warn (a_str) : sys.stderr.write('WARN: ' + a_str + '\n')
def stderr(a_str) : sys.stderr.write(a_str)
def die (a_str) : sys.stderr.write('ERROR: ' + a_str + '\n' ); sys.exit()

debug = 0

def weighted_choice_bisect_compile(items):
    """Returns function that produces weighted random choices among items.
    
       items is a hash, with keys and corresponding relative weights 
    """
    added_weights = []
    last_sum = 0
    for item, weight in items:
        # for debugging show that these weights are good.
        if debug & 2: print("%s:%.5f" % (item, weight))
        last_sum += weight
        added_weights.append(last_sum)
        if debug & 2: quit()
    # return a closure based random biased function
    def choice(rnd=random.random, bis=bisect.bisect):
        return items[bis(added_weights, rnd() * last_sum)][0]
    return choice

def winner_takes_all(items):
    """Returns function that returns the best valued choice among the items
    
       items is a hash, with keys and corresponding relative weights 
    """
    best_weight = None
    best_item = None
    for item, weight in items:
        # for debugging show that these weights are good.
        if debug & 2: print("%s:%.5f" % (item, weight))
        if best_weight is None or best_weight < weight:
            best_weight = weight  # Any weight is better than no weight.
            best_item = item

    # return a closure based random biased function
    def choice(rnd=random.random, bis=bisect.bisect):
        return items[bis(added_weights, rnd() * last_sum)][0]
    return choice

# def rand_choice(items):
#   return(...)

   # Food questions:
   #    keyword, 
   #        parameter type list, 
   #             ...
   #

# Some references
Food = 1
FoodCateg = 2
FoodInCateg = 3
Allergies = 4
Diseases = 5
Cuisine = 6

basic_out_templ_labels = {
    'like_food_2vars':0.3,
    'like_food_no_vars': 0.5,
    'do_you_eat_1var': 0.4,
    'do_you_eat_like': 0.6,
    'are_you_a_1var': 0.4,
    'foods_allergies': 0.3,
    'what_foods': 0.5,
    'foods_diseases': 0.5,
    'fav_cuisine': 0.5
}

basic_out_templ = {}
basic_out_templ['like_food_2vars']   = \
        [("What other %s do you like besides %s?", # e.g. (vegetables, carrots)
                (FoodCateg, FoodInCateg),   
                # Need to know that the FoodInCateg is isolated by 1st param 
                    (FoodCateg, FoodInCateg)
         ),
        0. ]   # Use this to help identify what is likely
               # to be the context of his answer.
               # e.g. I don't like it, but I like ...

basic_out_templ['like_food_no_vars'] = \
        [("Could you tell me about 3 vegetables you like?", 
            (None),
            (FoodCateg, Food)
         ), 
         0. ]

basic_out_templ['do_you_eat_1var']   = \
        [("Do you eat %s?", 
            (Food), 
            (Food)
         ), 
        0. ]    # e.g. meat, fish, 

basic_out_templ['do_you_eat_like']   = \
        [("Do you like %s?", 
            (Food),
            (Food)
         ), 
         0. ]   # e.g. meat, fish, carrots 

basic_out_templ['are_you_a_1var']    = \
        [ ("Are you a %s eater?", 
            (Food),
            (Food),
          ), 
        0. ] # meat

basic_out_templ['foods_allergies']   = \
        [ ("Are you allergic to any foods?", 
            (None),
            (Allergies, Food)
          ), 
        0. ] 

basic_out_templ['what_foods']        = \
        [("What foods?", 
            (None), 
            (Food)
         ), 
        0. ]

basic_out_templ['foods_diseases']    = \
        [("Do you have any diseases that affect what you eat?", 
            (None),
            (Diseases, Food)
         ), 
        0. ]

basic_out_templ['fav_cuisine']  = \
        [("Do you have a favorite cuisine?" , 
            (None),
            (Cuisine)
         ), 
        0. ]

food_categories = {}
food_categories = {'vegetable':0.8, 'poultry':0.5, 'meat':0.5, 
        'seafood':0.4, 'spices':0.2}

food_in_categories = {}
food_in_categories['vegetable'] = {'zuchini':0.1, 'carrots':06, 
        'onions':0.8, 'broccoli':0.5, 'garlic':0.7, 'colliflower':0.6
}
food_in_categories['poultry'] = {'chicken':0.7, 'turkey':0.5, 'duck':0.2}
food_in_categories['meat'] = {'pork':0.5, 'beef':0.5, 'lamb':0.3}
food_in_categories['spices'] = {'salt':0.3, 'pepper':0.5, 'cumin':0.6}
food_in_categories['seafood'] = {'sea bass':0.3, 'salmon':0.5, 'scallops':0.6}

cuisines = {'asian':0.3, 'cuban':0.4, 'thai':0.4, 
                    'japanese':0.6, 'american':0.7}

food_cuisine_contents = {}
# We can seed this with some ideas.
# These can be filled based on recipe statistics
food_cuisine_contents['asian'] = {
}

food_cuisine_contents['cuban'] = {
           'cumin': .4,
           'onions': .8,
           'garlic': .8,
           'beef': .7,
           'pork': .8,
           'white rice': .9,
           'pepper': .4,
           'olive oil': .4,
}

food_cuisine_contents['japanese'] = {
           'tuna': .5,
           'tofu': .5,
           'seaweed': .4,
           'octopus': .4,
           'white rice': .9,
}

food_cuisine_contents['italian'] = {
           'pasta': .9,
}

class user():
    """Help store all the information about each user"""
    def __init__(name):
        likes_list = []
        return()

    def describe_user():
        """prints out a description of what we know about this user"""
        return()

    def save_user():
        """saves user in the database"""
        return()

    def load_user():
        return()

class likes():
    def __init__():
        return()

    def gen_like(label, name, category=Food, like_value=0, certainty=0):
        self.label = label          # label for item
        self.category = category    # category type
        self.item = item            # item name
        self.like_value = like_value  # no. -1 to 1, -1:hate, 0:neutral, 1:love
        self.certainty = certainty  # number between 0 and 1, 0 don't know
                                    # 1 - totally certain.

    def resolution():
        """This function attempts to do deductions on likes and dislikes

           for instance a vegetarian - is likely not to eat meat, of lamb, or ...
           but might eat fish? --- i.e. a fish eating vegetarian
           or does not eat milk .... these are tough questions to ask, based on what
           is known

           This kind of resolution is statistical - people live with contradictions.
        """
        return(True)

    def increase_like(label):
        pass

    def fine_likes(label):
        pass

# class user_table:
#     food_likes:
#     cuisine_likes:
#
#   quest_type = basic_out_templ
#

# Generate all the randomizing functions - recompute when the weights change.
biased_rand_templ_lab = \
    weighted_choice_bisect_compile(basic_out_templ_labels.items())


rand_food_categ = \
    weighted_choice_bisect_compile(food_categories.items())
rand_food_in_categories = {}
for categ in food_categories.keys():
    rand_food_in_categories[categ] = \
            weighted_choice_bisect_compile(food_in_categories[categ].items())
rand_cuisine = \
            weighted_choice_bisect_compile(cuisines.items())

# Generate this with a for loop --- provides foods within a cuisine.
# biased_rand_cuisine = \
#    weighted_choice_bisect_compile(food_cuisine_contents{cuisine}.items())

for i in range(10):
    label = biased_rand_templ_lab()   # choose a question to ask at random.
    cuisine = rand_cuisine()  # choose a random cuisine
    categ = rand_food_categ()  # choose a random cuisine
    fun = rand_food_in_categories[categ]
    food = fun()


    # label,prob in basic_out_templ_labels.items(): 
    print("%d: %s, %s, %s, %s" % (i, label, cuisine, categ, food))

