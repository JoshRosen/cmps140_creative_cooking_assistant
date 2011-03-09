"""
Tests for the database.  Run with py.test.
"""
import unittest

from database import Database, DuplicateRecipeException, \
    DuplicateOntologyNodeException


class TestDatabaseQueries(unittest.TestCase):

    def setUp(self):
        self.db = Database("sqlite:///:memory:")
        # Sample recipe database
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

        # Sample ontology
        ontology_tuples = [
            ('ingredient', 'vegetable', 'root vegetable', 'potato'),
            ('ingredient', 'vegetable', 'root vegetable', 'yam'),
            ('ingredient', 'fruit', 'apple')
        ]
        for tup in ontology_tuples:
            self.db.add_ontology_node(tup)

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

    def test_ontology_navigation(self):
        """
        Test methods for navigating the ontology.
        """
        # The test database should only contain 7 IngredientNodes:
        assert self.db.get_ontology_nodes().count() == 7
        # Test roots nodes:
        ingredient_root = self.db.get_ontology_nodes('ingredient',
            only_root_nodes=True).one()
        assert ingredient_root.supertype == None
        assert ingredient_root.is_root()
        assert ingredient_root.is_subtype_of(ingredient_root)
        assert ingredient_root.is_subtype_of(ingredient_root.name)
        # Look at its subtypes:
        ingredient_subtype_names = [s.name for s in ingredient_root.subtypes]
        assert 'vegetable' in ingredient_subtype_names
        assert 'fruit' in ingredient_subtype_names
        # Test non-root nodes:
        yam = self.db.get_ontology_nodes('yam').one()
        assert yam.supertype.name == 'root vegetable'
        assert not yam.is_subtype_of('fruit')
        assert [n.name for n in yam.path_from_root] == \
               ['ingredient', 'vegetable', 'root vegetable', 'yam']
        assert [n.name for n in yam.siblings] == ['potato']

    def test_ontology_depth(self):
        """
        Make sure that the ontology's implementation of depth is correct.
        """
        for root in self.db.get_ontology_nodes(only_root_nodes=True):
            assert root.depth == 0
            for subtype in root.subtypes:
                assert subtype.depth == 1
                for subsubtype in subtype.subtypes:
                    assert subsubtype.depth == 2

    def test_search_deepest_first(self):
        """
        Ensure that db.get_ontology_nodes(deepest_first=True) works correctly.
        """
        nodes = self.db.get_ontology_nodes(deepest_first=True)
        depths = [n.depth for n in nodes]
        sorted_depths = list(reversed(sorted(depths)))
        assert sorted_depths == depths

class TestDatabaseExceptions(unittest.TestCase):

    def test_add_duplicate_recipes(self):
        db = Database("sqlite:///:memory:")
        assert len(db.get_recipes()) == 0
        db.add_from_recipe_parts({'title': 'cake', 'url': 'cake'})
        try:
            db.add_from_recipe_parts({'title': 'cake', 'url': 'cake'})
            assert False  # Should have got an exception
        except DuplicateRecipeException:
            pass
        assert len(db.get_recipes()) == 1

    def test_add_duplicate_ontology_nodes(self):
        db = Database("sqlite:///:memory:")
        assert db.get_ontology_nodes().count() == 0
        db.add_ontology_node(('dish', 'cake'))
        try:
            db.add_ontology_node(('dish', 'cake'))
            assert False  # Should have got an exception
        except DuplicateOntologyNodeException:
            pass
        assert db.get_ontology_nodes().count() == 2
        db.add_ontology_node(('ingredient', 'cake'))
        assert db.get_ontology_nodes().count() == 4
