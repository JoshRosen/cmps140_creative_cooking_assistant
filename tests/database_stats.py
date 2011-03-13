"""
Prints statistics for a database.  Some of these statistics may be useful when
deciding how to extend the ontology.
"""
from optparse import OptionParser
from database import Database, Ingredient, OntologyNode, \
    RecipeIngredientAssociation, Recipe
from sqlalchemy import desc, func
from sqlalchemy.orm import join


PARSER = OptionParser()
PARSER.add_option("--database", dest="database_url",
                  default='sqlite:///test_database.sqlite')


def unmatched_ingredients(db):
    """
    Return (names, num_recipes) ifor ingredients that are not matched with
    OntologyNodes.
    """
    recipe_count = func.count(RecipeIngredientAssociation._recipe_id)
    recipe_join = join(Ingredient, RecipeIngredientAssociation)
    query = (db._session.query(Ingredient, recipe_count)
                        .select_from(recipe_join)
                        .filter(Ingredient.ontology_node == None)
                        .group_by(Ingredient.id)
                        .order_by(desc(recipe_count)))
    return query


def main():
    """
    Main method for printing a bunch of statistics.
    """
    (options, args) = PARSER.parse_args()
    db = Database(options.database_url)

    # Counts of various relations:
    recipe_count = db._session.query(Recipe).count()
    ingredient_count = db._session.query(Ingredient).count()
    ontology_count = db._session.query(OntologyNode).count()
    print "Stats for %s" % options.database_url
    print
    print "      Recipes: %i" % recipe_count
    print "  Ingredients: %i" % ingredient_count
    print "OntologyNodes: %i" % ontology_count
    print
    # Unmatched ingredients
    unmatched_count = unmatched_ingredients(db).count()
    percent_unmatched = unmatched_count / (ingredient_count * 1.0)
    print "%.2f%% of Ingredients are unmatched with OntologyNodes" % \
        (percent_unmatched * 100)
    print
    ingred_limit = 50
    print "Top %i ingredients without matching OntologyNodes:" % ingred_limit
    unmatched = unmatched_ingredients(db).limit(ingred_limit).all()
    print " Count Ingredient Name"
    for (ingredient, recipe_count) in unmatched:
        print "%6i %s" % (recipe_count, ingredient.name)


if __name__ == '__main__':
    main()
