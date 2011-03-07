"""
Import the ontology into the database.  This should be run before the recipes
are added to the database, so that ingredients can be properly linked to nodes
in the ingredient ontology.
"""
from database import Database, DuplicateOntologyNodeException
from nlu import normalize_ingredient_name
import os
import logging

ONTOLOGY_DIR = os.path.join(os.path.dirname(__file__), 'ontology')
ONTOLOGY_FILENAMES =  os.listdir(ONTOLOGY_DIR)


def normalize_ontology_name(name):
    return normalize_ingredient_name(name).replace('_', ' ')


def main():
    db = Database('sqlite:///test_database.sqlite')

    for filename in ONTOLOGY_FILENAMES:
        with open(os.path.join(ONTOLOGY_DIR, filename)) as ontology_file:
            for line in ontology_file:
                node = eval(line)
                node = [normalize_ontology_name(x) for x in node]
                try:
                    db.add_ontology_node(node)
                except DuplicateOntologyNodeException:
                    logging.warn("Skipping duplicate node %s" % node)
    logging.info("The ontology contains %i nodes" %
        db.get_ontology_nodes().count())

if __name__ == "__main__":
    main()
"""
print "The ontology contains %i nodes" % db.get_ontology_nodes().count()

node_names = set(n.name for n in db.get_ontology_nodes())
ingredient_names = set(i.name for i in db.get_ingredients())
for ingredient in ingredient_names:
    for node in node_names:
        if ingredient.find(node) and re.search(r"\b" + node + r"\b", ingredient):
            print "Node %s, Ingredient %s" % (node, ingredient)
            break

print "Num_ingredients: %i" % len(ingredient_names)
print "Matched with ontology: %i" % len(ingredient_names.intersection(node_names))
#print ingredient_names.intersection(node_names)

#for name in ingredient_names:
#    if name not in node_names:
#        print name
#for name in node_names:
#    if name not in ingredient_names:
#        print name
"""
