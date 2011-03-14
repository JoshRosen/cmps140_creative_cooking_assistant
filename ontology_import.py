"""
Import the ontology into the database.  This should be run before the recipes
are added to the database, so that ingredients can be properly linked to nodes
in the ingredient ontology.
"""
from database import Database, DuplicateOntologyNodeException, OntologyNode
from nlu import normalize_ingredient_name
import os
import logging
from optparse import OptionParser

ONTOLOGY_DIR = os.path.join(os.path.dirname(__file__), 'ontology')
ONTOLOGY_FILENAMES =  os.listdir(ONTOLOGY_DIR)


def normalize_ontology_name(name):
    return normalize_ingredient_name(name).replace('_', ' ')


def main():
    parser = OptionParser()
    parser.add_option("--database", dest="database_url",
                      default='sqlite:///test_database.sqlite')
    (options, args) = parser.parse_args()
    db = Database(options.database_url)

    for filename in ONTOLOGY_FILENAMES:
        with open(os.path.join(ONTOLOGY_DIR, filename)) as ontology_file:
            for line in ontology_file:
                if line.strip()[0] == '#':
                    logging.warn("Skipping comment: '%s'" % line.strip())
                    continue
                node = eval(line)
                node = [normalize_ontology_name(x) for x in node]
                try:
                    db.add_ontology_node(node)
                except DuplicateOntologyNodeException:
                    logging.warn("Skipping duplicate node %s" % node)
    logging.info("The ontology contains %i nodes" %
        db._session.query(OntologyNode).count())


if __name__ == "__main__":
    main()
