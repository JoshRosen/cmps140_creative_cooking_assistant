"""
Tests for the database.  Run with py.test.
"""
import os.path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from database import Database


def test_printing_unicode_from_db():
    """
    When printing text from the database, ignore non-ASCII characters.
    """
    db = Database("sqlite:///:memory:")
    recipe_parts = {
        'title' : u"World-Famous Chocolate-Covered Bacon\u2122",
        'url' : ""
    }
    db.add_from_recipe_parts(recipe_parts)
    recipe = db.get_recipes()[0]
    assert recipe.title == "World-Famous Chocolate-Covered Bacon"
    print recipe
