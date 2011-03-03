"""
Tests for the database.  Run with py.test.
"""
import unittest

from database import Database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = Database("sqlite:///:memory:")
        recipe_parts = {
            'title' : u"World-Famous Chocolate-Covered Bacon\u2122",
            'url' : "chocolate_bacon",
            'ingredients' : ['1 slice bacon', '1 package chocolate']
        }
        self.db.add_from_recipe_parts(recipe_parts)
        recipe_parts = {
            'title' : u"Chocolate-covered apple",
            'url' : "chocolate_apple",
            'ingredients' : ['1 medium apple', '1 package chocolate']
        }
        self.db.add_from_recipe_parts(recipe_parts)
        recipe_parts = {
            'title' : u"Peach Pie",
            'url' : "apple_pie",
            'ingredients' : ['1 pie crust', '14 peaches']
        }
        self.db.add_from_recipe_parts(recipe_parts)

    def test_printing_unicode_from_db(self):
        """
        When printing text from the database, ignore non-ASCII characters.
        """
        recipe = self.db.get_recipes(include_ingredients=['bacon'])[0]
        assert recipe.title == "World-Famous Chocolate-Covered Bacon"
        print recipe  # To test that we don't crash on print.

    def test_search_by_multiple_ingredients(self):
        # Include multiple ingredients
        query = {'include_ingredients': ['bacon', 'chocolate']}
        recipes = self.db.get_recipes(**query)
        assert len(recipes) == 1
        assert recipes[0].title == "World-Famous Chocolate-Covered Bacon"

        # Exclude multiple ingredients
        query = {'exclude_ingredients': ['bacon', 'apple']}
        recipes = self.db.get_recipes(**query)
        assert len(recipes) > 0
        for recipe in recipes:
            ingredient_names = [i.ingredient.name for i in recipe.ingredients]
            assert 'bacon' not in ingredient_names
            assert 'apple' not in ingredient_names
        assert "Peach Pie" in (r.title for r in recipes)
