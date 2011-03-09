"""
Object-based interface to the database used by the chatbot.

The database is accessed through the Database object:

>>> db = Database("sqlite:///:memory:")

(Note: for now, sqlite is the only supported database; support for other
databases will require adding string length constraints to some of the database
columns.)

Recipes are added to the database using dictionaries.  The allrecipes.py file
contains code to generate dictionaries from scraped recipes.  For testing, you
can create them by hand:

>>> recipe_parts = {
... 'title' :  'Peanut butter and jelly sandwich',
... 'author' : 'Anonymous',
... 'url' : 'http://example.com/pbj.html',
... 'prep_time' : 5,
... 'total_time' : 5,
... 'servings' : 1,
... 'ingredients' : [
...     '1 cup peanut butter',
...     '1 tablespoon jelly',
...     '2 slices sliced bread'],
... 'steps' : [
...     'Remove bread from package',
...     'Spread peanut butter and jelly onto each slice of bread.',
...     'Combine slices of bread, optionally remove crust, and eat.']
... }
>>> db.add_from_recipe_parts(recipe_parts)

You can search for recipes based on the ingredients that they contain:

>>> recipes = db.get_recipes(include_ingredients=['spam'])
>>> len(recipes)
0
>>> recipes = db.get_recipes(include_ingredients=['peanut butter'],
...                          exclude_ingredients=['chicken'],
...                          num_ingredients=3)
>>> len(recipes)
1

The results of the query are returned as a list of Recipe objects.  You can
access a recipe's ingredients through its ingredients attribute, which is
a list of RecipeIngredientAssociation objects.  Each object represents a line
containing an ingredient in the recipe.

>>> recipes[0].ingredients[0].ingredient.name
'peanut butter'
>>> recipes[0].ingredients[0].unit
'cup'
>>> recipes[0].ingredients[0].quantity
'1'
>>> recipes[0].ingredients[2].modifiers
'sliced'

The RecipeIngredientAssociation objects can be printed:

>>> for ingredient in recipes[0].ingredients:
...     print ingredient
1 cup peanut butter
1 tablespoon jelly
2 slices sliced bread

>>> print recipes[0].steps_text
Remove bread from package
Spread peanut butter and jelly onto each slice of bread.
Combine slices of bread, optionally remove crust, and eat.

You can construct some very complicated queries:

>>> recipes = db.get_recipes(include_ingredients=['bacon', 'chocolate'],
...     exclude_ingredients=['blueberries'], prep_time=5, cook_time=(None, 20),
...     total_time=(10, 30), num_steps=(3, None), num_ingredients=6,
...     include_cuisines=['Italian'], exclude_cuisines=['Indian'])

In many cases, you'll want to incrementally refine queries.  You can specify
your search criteria as a dictionary, then use the special **expression call
syntax (http://docs.python.org/reference/expressions.html#calls):

>>> search_criteria = {
... 'include_ingredients': ['peanut butter'],
... 'exclude_ingredients': ['chicken'],
... 'num_ingredients': 3
... }

>>> recipes = db.get_recipes(**search_criteria)
>>> recipes[0].title
'Peanut butter and jelly sandwich'

Given the ingredient object, you can also find which recipes use it:

>>> db.get_ingredients('bread').first().recipes[0].title
'Peanut butter and jelly sandwich'

For the full details on the search capabilities, see the documentation for the
get_recipes() method.
"""
from collections import defaultdict
import re

from sqlalchemy import create_engine, Table, Column, Integer, \
    String, ForeignKey, UniqueConstraint
from sqlalchemy.sql.expression import between, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship, sessionmaker, join, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.interfaces import PoolListener

from nlu import extract_ingredient_parts, normalize_ingredient_name
from nltk import word_tokenize
from RecipeCategorizer import get_cuisine


Base = declarative_base()


recipe_cuisines = Table('recipe_cuisines', Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('cuisines_id', Integer, ForeignKey('cuisines.id'))
)


class Database(object):
    """
    Represents a connection to a specific database and provides convenience
    methods for obtaining objects from that database.
    """

    def __init__(self, database_url):
        """
        Connect to a database, specified by a database URL.
        For the URL format, see
        http://www.sqlalchemy.org/docs/core/engines.html#database-urls
        """
        self._database_url = database_url
        # See http://groups.google.com/group/sqlalchemy/browse_thread/thread/430371a20fd69468
        class SetTextFactory(PoolListener):
            def connect(self, dbapi_con, con_record):
                dbapi_con.text_factory = \
                    lambda x: x.decode('ascii', 'ignore').encode()
        self._engine = create_engine(self._database_url,
            listeners=[SetTextFactory()])
        self._sessionmaker = sessionmaker(bind=self._engine)
        self._session = self._sessionmaker()
        self.create_database_schema()
        self._ontology_regex = None # This is cached for performance.

    def __getstate__(self):
        # When pickling this object, use the database url as the pickled
        # representation.
        return self._database_url

    def __setstate__(self, database_url):
        # When unpickling this object, connect to the database_url stored
        # during pickling.
        self.__init__(database_url)

    def create_database_schema(self):
        """
        If necessary, creates the tables in the database.
        """
        Base.metadata.create_all(self._engine)

    # Recipe- and ingredient-related methods

    def _new_ingredient(self, ingredient_name):
        """
        Create a new Ingredient object with the given name and link it to the
        ontology.
        """
        ingredient = Ingredient(ingredient_name)
        # TODO: this will behave incorrectly once we add non-ingredients to the
        # ontology.  I'll fix this later.
        # Heuristic: try the longest match first.  If ontology nodes have the
        # same name, prefer the deper node.
        if not self._ontology_regex:
            nodes = self.get_ontology_nodes().all()
            def sort_function(x, y):
                return cmp(len(y.name), len(x.name)) or cmp(y.depth, x.depth)
            nodes.sort(sort_function)
            self._ontology_regex = \
                re.compile('|'.join('\\b%s\\b' % n.name for n in nodes))
        match = self._ontology_regex.match(ingredient_name)
        if match and match.group(0):
            node_name = match.group(0)
            ontology_node = self.get_ontology_nodes(node_name, deepest_first=True).first()
            ingredient.ontology_node = ontology_node
            #print "Matched %s with Ontology %s" % (ingredient_name, ontology_node.name)
        return ingredient

    def add_from_recipe_parts(self, recipe_parts):
        """
        Add a recipe from a dictionary describing the recipe.  The dictionary
        could be generated by a scraper.  For an example, see the
        extract_recipe_parts function in allrecipes.py.

        Raises a DuplicateRecipeException when inserting a duplicate recipe.
        """
        self._add_from_recipe_parts(recipe_parts)
        self._session.commit()

    def _add_from_recipe_parts(self, recipe_parts):
        """
        Adds a recipe, but doesn't commit the transaction.
        """
        # First, make sure that we're not inserting a duplicate record.
        # Duplicates are considered to be recipes with the same url.
        duplicate = self._session.query(Recipe).\
                        filter_by(url=recipe_parts['url'])
        if duplicate.first():
            raise DuplicateRecipeException(
                "Recipe with url %s already exists." % recipe_parts['url'])
        recipe = Recipe()
        recipe_parts = defaultdict(str, recipe_parts)
        recipe.title = recipe_parts['title']
        recipe.url = recipe_parts['url']
        recipe.author = recipe_parts['author']
        recipe.description = recipe_parts['description']
        recipe.num_steps = recipe_parts['num_steps']
        recipe.servings = recipe_parts['servings']
        recipe.prep_time = recipe_parts['prep_time']
        recipe.cook_time = recipe_parts['cook_time']
        recipe.total_time = recipe_parts['total_time']
        recipe.ingredients_text = "\n".join(recipe_parts['ingredients'])
        recipe.steps_text = "\n".join(recipe_parts['steps'])

        for ingredient_string in recipe_parts['ingredients']:
            ingredient_parts = extract_ingredient_parts(ingredient_string)
            if not ingredient_parts:
                continue
            ingredient_parts = defaultdict(lambda: None, ingredient_parts)
            ingredient = self.get_ingredients(
                name=ingredient_parts['base_ingredient']).first()
            if not ingredient:
                ingredient = self._new_ingredient(ingredient_parts['base_ingredient'])
                self._session.add(ingredient)
            unit = ingredient_parts['unit']
            quantity = ingredient_parts['quantity']
            modifiers = ingredient_parts['modifiers']
            assoc = RecipeIngredientAssociation(ingredient, unit, quantity,
                                                modifiers)
            recipe.ingredients.append(assoc)

        # The ingredient count is stored as a part of the reicpe to avoid
        # expensive subqueries when filtering recipes based on the number of
        # ingredients that they contain.  It's unlikely that recipes would be
        # modified after they're imported, but there should probably be
        # a trigger to ensure that this count remains up to date.
        # The count is set after processing the ingredient string to prevent
        # headings like "CRUST: " from contributing to the ingredient count.
        recipe.num_ingredients = len(recipe.ingredients)

        # Add cuisines
        for cuisine_name in recipe._determine_cuisines():
            cuisine = self.get_cuisines(name=cuisine_name).first()
            if not cuisine:
                cuisine = Cuisine(cuisine_name)
                self._session.add(cuisine)
            recipe.cuisines.append(cuisine)

        self._session.add(recipe)

    def get_recipes(self, include_ingredients=(), exclude_ingredients=(),
                    include_cuisines=(), exclude_cuisines=(),
                    prep_time=None, cook_time=None, total_time=None,
                    num_steps=None, num_ingredients=None):
        """
        Get recipes matching the given criteria.

        Numeric attributes, like total_time, can be specified as single values
        (to retreive exact matches) or (min, max) tuples that define ranges
        which include their endpoints.  To specify just a maximum or minimum,
        set the other value to None.

        For example, to find recipes with a total time of 1/2 to 1 hours:
        >>> db = Database("sqlite:///:memory:")
        >>> recipes = db.get_recipes(total_time=(30, 60))

        Or, to find recipes that take up to 15 minutes to prepare:
        >>> recipes = db.get_recipes(prep_time=(None, 15))

        To find recipes that have exactly 5 steps:
        >>> recipes = db.get_recipes(num_steps=5)

        To find Italian recipes:
        >>> recipes = db.get_recipes(include_cuisines=["Italian"])
        """
        # Normalize ingredient names, so that they match the names stored in
        # the database.
        include_ingredients = \
            [normalize_ingredient_name(i) for i in include_ingredients]
        exclude_ingredients = \
            [normalize_ingredient_name(i) for i in exclude_ingredients]
        # Construct the query
        query = self._session.query(Recipe)
        # Handle ingredient inclusion and exclusion
        if include_ingredients or exclude_ingredients:
            double_join = join(RecipeIngredientAssociation, Recipe)
            triple_join = join(double_join, Ingredient)
            join_query = query.select_from(triple_join)
            query = join_query
            for ingredient_name in include_ingredients:
                query = query.intersect(
                    join_query.filter(Ingredient.name == ingredient_name))
            for ingredient_name in exclude_ingredients:
                query = query.except_(
                    join_query.filter(Ingredient.name == ingredient_name))
        # Handle cuisine inclusion and exclusion:
        # TODO: cuisine names should probably be normalized before querying, so
        # lowercase 'italian' matches 'Italian'.
        if include_cuisines or exclude_cuisines:
            for cuisine_name in include_cuisines:
                query = query.filter(Recipe.cuisines.any(
                    Cuisine.name == cuisine_name))
            for cuisine_name in exclude_cuisines:
                query = query.filter(Recipe.cuisines.any(
                    Cuisine.name != cuisine_name))
        # Handle ranges searches over simple numeric attributes, like
        # total_time or num_steps
        if total_time != None:
            query = query.filter(_range_predicate(Recipe.total_time,
                total_time))
        if cook_time != None:
            query = query.filter(_range_predicate(Recipe.cook_time, cook_time))
        if prep_time != None:
            query = query.filter(_range_predicate(Recipe.prep_time, prep_time))
        if num_steps != None:
            query = query.filter(_range_predicate(Recipe.num_steps, num_steps))
        if num_ingredients != None:
            query = query.filter(_range_predicate(Recipe.num_ingredients,
                num_ingredients))
        return query.all()

    def get_ingredients(self, name=None):
        """
        Get ingredients matching the given criteria.
        """
        query = self._session.query(Ingredient)
        if name != None:
            name = normalize_ingredient_name(name)
            query = query.filter_by(name=name)
        return query

    def get_cuisines(self, name=None):
        """
        Get cuisines matching the given criteria.
        """
        query = self._session.query(Cuisine)
        if name != None:
            query = query.filter_by(name=name)
        return query

    # Ontology-related methods

    def add_ontology_node(self, ontology_tuple):
        """
        Add an ontology node from a tuple representing the path from the new
        node to a root of a tree in the ontology.

        Raises a DuplicateOntologyNodeException when adding a duplicate node.
        """
        root_name = ontology_tuple[0]
        depth = 0
        try:
            root = self._session.query(OntologyNode).filter_by(name=root_name,
                supertype=None).one()
        except NoResultFound:
            root = OntologyNode(root_name)
            root.depth = 0
            #self._session.add(OntologyNode)
        added_nodes = False
        last_node = root
        depth = 1
        for node_name in ontology_tuple[1:]:
            try:
                node = self._session.query(OntologyNode).filter_by(
                    name=node_name, supertype=last_node).one()
            except NoResultFound:
                node = OntologyNode(node_name)
                node.supertype = last_node
                node.depth = depth
                depth += 1
                added_nodes = True
            last_node = node
        if added_nodes:
            self._session.add(last_node)
            self._session.commit()
            self._ontology_regex = None  # Expire cached regex due to new node.
        else:
            raise DuplicateOntologyNodeException(
                'OntologyNode %s already exists.' % str(ontology_tuple))

    def get_ontology_nodes(self, name=None, only_root_nodes=False,
        deepest_first=False):
        """
        Get ontology nodes matching the given criteria.
        """
        query = self._session.query(OntologyNode)
        if name != None:
            query = query.filter_by(name=name)
        if only_root_nodes:
            query = query.filter_by(supertype=None)
        if deepest_first:
            query = query.order_by(desc(OntologyNode.depth))
        return query


class RecipeIngredientAssociation(Base):
    """
    Associates an ingredient with a recipe.  Contains information about the
    association, such as the amount of the ingredient or modifiers (such as
    'chopped' or 'fresh').
    """
    __tablename__ = 'recipe_ingredient_association'
    # These primary key constraints allow a recipe to list the same ingredient
    # twice, e.g. 'chopped apples' and 'pureed apples' as separate ingredients.
    recipe_ingredient_association_id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    recipe = relationship("Recipe")
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'))
    ingredient = relationship("Ingredient", backref="ingredient_associations")
    quantity = Column(String)
    unit = Column(String)
    modifiers = Column(String)

    def __init__(self, ingredient, unit, quantity, modifiers):
        self.ingredient = ingredient
        self.unit = unit
        self.quantity = quantity
        self.modifiers = modifiers

    def __repr__(self):
        return "<RecipeIngredientAssociation(%s, %s)>" % \
            (self.recipe.title, self.ingredient.name)

    def __str__(self):
        parts = [self.quantity, self.unit, self.modifiers,
            self.ingredient.name]
        return ' '.join(x for x in parts if x)


class Recipe(Base):
    """
    Represents a single recipe.
    """
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String, nullable=False)
    author = deferred(Column(String), group='recipe_text')
    description = deferred(Column(String), group='recipe_text')
    ingredients = relationship(RecipeIngredientAssociation)
    cuisines = relationship('Cuisine', secondary=recipe_cuisines,
                            backref='recipes')
    num_steps = Column(Integer)
    num_ingredients = Column(Integer)
    ingredients_text = deferred(Column(String), group='recipe_text')
    steps_text = deferred(Column(String), group='recipe_text')
    servings = Column(String)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    total_time = Column(Integer)

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return "<Recipe(%s)>" % self.title

    def _determine_cuisines(self):
        """
        Determine the cuisines for this recipe.  This is a private method used
        during recipe import.
        """
        # For now, store only the top cuisine (or multiple cuisines in the
        # event of a tie).  A more robust approach would store cuisines whose
        # scores are in some top percentile.
        cuisine_title = self.title
        cuisine_description = self.description
        cuisine_ingredients = []
        for ingredient_assoc in self.ingredients:
            cuisine_ingredients.append(ingredient_assoc.ingredient.name)
        cuisine_scores = get_cuisine(cuisine_title, 
            cuisine_description, cuisine_ingredients)
        if not cuisine_scores:
            return []
        max_score = max(cuisine_scores.values())
        result = []
        for cuisine in cuisine_scores.keys():
            if cuisine_scores[cuisine] == max_score:
                result.append(cuisine)
        return result


class OntologyNode(Base):
    """
    Represents a node in a tree in the ontology.  Given an OntologyNode, you
    can explore its relationship to other nodes in the ontology.

    >>> db = Database("sqlite:///:memory:")
    >>> db.add_ontology_node(('ingredient', 'fruit', 'apple'))
    >>> db.add_ontology_node(('ingredient', 'fruit', 'orange'))
    >>> db.add_ontology_node(('ingredient', 'vegetable', 'potato'))

    >>> apple = db.get_ontology_nodes('apple').one()
    >>> apple.is_root()
    False
    >>> [s.name for s in apple.siblings]
    ['orange']
    >>> apple.is_subtype_of('ingredient')
    True
    >>> apple.is_subtype_of('vegetable')
    False
    >>> [s.name for s in apple.path_from_root]
    ['ingredient', 'fruit', 'apple']
    """
    __tablename__ = 'ontology_nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    supertype_id = Column(Integer, ForeignKey('ontology_nodes.id'))
    subtypes = relationship("OntologyNode", backref=backref('supertype',
        remote_side=id))
    # This depth will break if the node is relocated in the tree.
    depth = Column(Integer, nullable=False)
    # Two different OntologyNodes may have the same name if they differ in
    # path_from_root, hence these uniqueness constraints.  As a base case,
    # root nodes must have distinct names.  Recursively, nodes with the same
    # name are different if their supertypes are different.
    __table_args__ = (
        UniqueConstraint('name', 'supertype_id'),
        {}
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<OntologyNode(%s)>" % self.name

    def is_subtype_of(self, ontology_node_or_name):
        """
        Return True if this OntologyNode is a subtype of the given ontology
        node or an ontology node with the given name, False otherwise.
        """
        # TODO: normalize ingredient type names so this search is less brittle.
        if isinstance(ontology_node_or_name, OntologyNode):
            if self == ontology_node_or_name:
                return True
        else:
            if self.name == ontology_node_or_name:
                return True
        if not self.supertype:
            return False
        else:
            return self.supertype.is_subtype_of(ontology_node_or_name)

    def is_root(self):
        """
        Return True if this OntologyNode is the root of a tree in the ontology.
        """
        return self.supertype == None

    @property
    def path_from_root(self):
        """
        A list describing the path from the root of a tree in the ontology to
        this OntologyNode.
        """
        path = [self]
        node = self.supertype
        while node:
            path.insert(0, node)
            node = node.supertype
        return path

    @property
    def tree_diagram(self):
        """
        Returns a string containing a printable representation of the subtree
        rooted at this node.
        """
        lines = [self.name]
        subtypes = list(self.subtypes)
        subtypes.sort(lambda x, y: cmp(x.name, y.name))
        for subtype in subtypes:
            lines.extend("    " + l for l in subtype.tree_diagram.split('\n'))
        return '\n'.join(lines)

    @property
    def siblings(self):
        """
        An iterable that lists the siblings of this OntologyNode.  An
        OntologyNode is not considered its own sibling.
        """
        supertype = self.supertype
        if supertype:
            return set(supertype.subtypes) - set([self])
        else:
            return []


class Ingredient(Base):
    """
    Represents a single ingredient as the food item itself, not a quantity of a
    prepared or modified ingredient.  For example, Ingredient can represent an
    apple, but not 3/4 cup of finely chopped apples.
    """
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ontology_node_id = Column(Integer, ForeignKey('ontology_nodes.id'))
    ontology_node = relationship("OntologyNode", backref='ingredients')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Ingredient(%s)>" % self.name

    @property
    def recipes(self):
        """
        Return the list of recipes that use this ingredient.
        """
        return [a.recipe for a in self.ingredient_associations]


class Cuisine(Base):
    """
    Represents a cuisine, such as "Indian" or "Italian".
    """
    __tablename__ = 'cuisines'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Cuisine(%s)>" % self.name


class DatabaseException(Exception):
    """
    Base class for exceptions thrown by the database.
    """
    pass


class DuplicateRecipeException(DatabaseException):
    """
    Thrown when trying to add a duplicate recipe to the database.
    """
    pass


class DuplicateOntologyNodeException(DatabaseException):
    """
    Thrown when trying to add a duplicate ontology node to the database.
    """
    pass


def _range_predicate(attribute, val_range):
    """
    Accepts an attribute and a tuple (min, max), and returns a predicate to
    find items whose attribute values fall within that range.  The range
    includes the endpoints.

    This is a private helper function used to avoid cluttering get_recipes().
    """
    if not hasattr(val_range, '__iter__'):
        return attribute == val_range
    else:
        if len(val_range) != 2:
            raise ValueError(
                "Invalid range %s; valid ranges are (min, max) tuples."
                % str(val_range))
        (min_val, max_val) = val_range
        if min_val != None and max_val != None:
            return between(attribute, min_val, max_val)
        elif min_val != None:
            return attribute >= min_val
        else:
            return attribute <= max_val
