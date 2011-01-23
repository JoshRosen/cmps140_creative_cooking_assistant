"""
Object-based interface to the database used by the chatbot.
"""

from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


recipe_ingredients = Table('recipe_ingredients', Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)


recipe_categories = Table('recipe_categories', Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
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
        self._engine = create_engine(database_url)
        self._sessionmaker = sessionmaker(bind=self._engine)
        self._session = self._sessionmaker()

    def create_database_schema(self):
        """
        If necessary, creates the tables in the database.
        """
        Base.metadata.create_all(self._engine)

    def get_ingredients_by_name(self, ingredient_name):
        """
        Returns a list of Ingredient objects matching ingredient_name, or an
        empty list if no matching ingredient objects were found.
        """
        return self._session.query(Ingredient).filter_by(name=ingredient_name)


class Recipe(Base):
    """
    Represents a single recipe.
    """
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String, nullable=False)
    #slug = Column(String, nullable=False, unique=True)
    author = Column(String)
    description = Column(String)
    ingredients = relationship('Ingredient', secondary=recipe_ingredients,
                               backref='recipes')
    categories = relationship('Category', secondary=recipe_categories,
                               backref='recipes')
    num_steps = Column(Integer)
    recipe_text = Column(String)
    servings = Column(String)
    prep_time = Column(Integer)
    cook_time = Column(Integer)
    total_time = Column(Integer)

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return "<Recipe(%s)>" % self.title


class Ingredient(Base):
    """
    Represents a single ingredient as the food item itself, not a quantity of a
    prepared or modified ingredient.  For example, Ingredient can represent an
    apple, but not 3/4 cup of finely chopped apples.
    """
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Ingredient(%s)>" % self.name


class Category(Base):
    """
    Represents a category that a recipe can belong to, like Breakfast or
    Indian.
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Category(%s)>" % self.name
