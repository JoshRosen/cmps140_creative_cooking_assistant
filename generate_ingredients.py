"""
Generates the ingredients.txt file by dumping the ingredients from the db.
"""
from database import Database


def _sanitize_name(name):
    """
    Remove words after commas and in parentheses.
    >>> _sanitize_name("apples  (organic)  ")
    'apples'
    >>> _sanitize_name("spinach, fresh or frozen")
    'spinach'
    """
    comma_pos = name.find(',')
    paren_pos = name.find('(')
    if comma_pos != -1:
        name = name[:comma_pos]
    if paren_pos != -1:
        name = name[:paren_pos]
    return name.strip()


def main():
    db = Database("sqlite:///database.sqlite")
    names = set([_sanitize_name(i.name) for i in db.get_ingredients()])
    ingredients_file = open('wordlists/ingredients.txt', 'w')
    for name in names:
        ingredients_file.write('%s\n' % name)


if __name__ == "__main__":
    main()
