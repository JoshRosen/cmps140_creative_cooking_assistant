"""
Tests for the database.  Run with py.test.
"""
import unittest

from database import Database, DuplicateRecipeException, \
    DuplicateOntologyNodeException, OntologyNode


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
            ('ingredient', 'fruit', 'apple'),
            ('cuisine', 'vegetable')
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
        assert self.db._session.query(OntologyNode).count() == 9
        # Test roots nodes:
        ingredient_root = \
            self.db._session.query(OntologyNode).filter_by(name='ingredient').one()
        assert ingredient_root.supertype == None
        assert ingredient_root.is_root()
        assert ingredient_root.is_subtype_of(ingredient_root)
        assert ingredient_root.is_subtype_of(ingredient_root.name)
        # Look at its subtypes:
        ingredient_subtype_names = [s.name for s in ingredient_root.subtypes]
        assert 'vegetable' in ingredient_subtype_names
        assert 'fruit' in ingredient_subtype_names
        # Test non-root nodes:
        yam = self.db._session.query(OntologyNode).filter_by(name='yam').one()
        assert yam.supertype.name == 'root vegetable'
        assert not yam.is_subtype_of('fruit')
        assert [n.name for n in yam.path_from_root] == \
               ['ingredient', 'vegetable', 'root vegetable', 'yam']
        assert [n.name for n in yam.siblings] == ['potato']

    def test_get_ontology_node(self):
        """
        Tests for db.get_ontology_node().
        """
        # Whitespace should not matter:
        node = self.db.get_ontology_node('ingredient')
        assert node.name == 'ingredient'
        node = self.db.get_ontology_node('   ingredient    ')
        assert node.name == 'ingredient'
        # Pluralization and capitalization should not matter:
        node = self.db.get_ontology_node('   Cuisines ')
        assert node.name == 'cuisine'
        # If a word is both a cuisine and an ingredient (like 'vegetable' in
        # this example ontology), then the ingredient should take precedence if
        # there are other words in the input (like 'fresh') and the cuisine
        # should take precedence if it is the only word in the input:
        node = self.db.get_ontology_node('   fresh   vegetable    ')
        assert node.name == 'vegetable'
        assert node.supertype.name == 'ingredient'
        # Here, cuisine should take precedence.
        node = self.db.get_ontology_node('   vegetable    ')
        assert node.name == 'vegetable'
        assert node.supertype.name == 'cuisine'
        # Check that substrings do not trigger false positives
        node = self.db.get_ontology_node('  XvegetableX ')
        assert node == None

    def test_ontology_depth(self):
        """
        Make sure that the ontology's implementation of depth is correct.
        """
        for root in (self.db._session
            .query(OntologyNode).filter_by(supertype=None)):
            assert root.depth == 0
            for subtype in root.subtypes:
                assert subtype.depth == 1
                for subsubtype in subtype.subtypes:
                    assert subsubtype.depth == 2

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
        assert db._session.query(OntologyNode).count() == 0
        db.add_ontology_node(('dish', 'cake'))
        try:
            db.add_ontology_node(('dish', 'cake'))
            assert False  # Should have got an exception
        except DuplicateOntologyNodeException:
            pass
        assert db._session.query(OntologyNode).count() == 2
        db.add_ontology_node(('ingredient', 'cake'))
        assert db._session.query(OntologyNode).count() == 4

    def test_include_and_exclude_fail_on_string_argument(self):
        db = Database("sqlite:///:memory:")
        try:
            db.get_recipes(include_ingredients='apple')
            assert False  # Should have got an exception
        except ValueError:
            pass
        try:
            db.get_recipes(exclude_cuisines='Italian')
            assert False  # Should have got an exception
        except ValueError:
            pass
