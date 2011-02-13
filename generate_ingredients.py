"""
Generates the ingredients.txt file by dumping the ingredients from the db.
"""

from database import Database
import re

ingredients_file = open('wordlists/ingredients.txt', 'w')

db = Database("sqlite:///database.sqlite")
db.create_database_schema()

recipes = db.get_recipes()

ingredients = set()
for recipe in recipes:
    for ingredient in recipe.ingredients:
        ingredients.add(ingredient.ingredient)

for ingredient in ingredients:
    # santitize: remove words after commas and in elipses
    ingredient_name = ingredient.name
    comma_pos = ingredient.name.find(',')
    elipse_pos = ingredient.name.find('(')
    if comma_pos != -1: ingredient_name = ingredient_name[:comma_pos]
    if elipse_pos != -1: ingredient_name = ingredient_name[:elipse_pos]
    ingredients_file.write('%s\n' % ingredient_name)
