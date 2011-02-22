"""
Generates the ingredients.txt file by dumping the ingredients from the db.
"""
from database import Database

def main():
    db = Database("sqlite:///database.sqlite")
    names = set([c.name for c in db.get_cuisines()])
    categories_file = open('wordlists/cuisines.txt', 'w')
    for name in names:
        categories_file.write('%s\n' % name)


if __name__ == "__main__":
    main()
