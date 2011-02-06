"""
Tools for for extracting recipes from AllRecipes.com.

AllRecipes.com provides an XML sitemap file containing links to every recipe in
the site at http://allrecipes.com/recipedetail.xml.

Run this module to add recipes to a database.
"""

import lxml.html
from lxml import etree
from collections import defaultdict
import glob
import logging
from optparse import OptionParser
import os
import sys

from nlu import time_to_minutes
from database import Database, DuplicateRecipeException

SITEMAP_XML_NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def get_recipe_urls(sitemap_file):
    """
    Return a list of recipe urls from the AllRecipes.com sitemap file,
    which can be downloaded from http://allrecipes.com/recipedetail.xml
    """

    root = etree.parse(sitemap_file)
    return [e.text for e in root.iter(SITEMAP_XML_NAMESPACE + "loc")]


def extract_recipe_parts(recipe_detail_page):
    """
    Example code demonstrating how to get different parts of the recipe from an
    AllRecipes.com detail page.
    """
    # This will be replaced with a real Recipe object later.  Here, I'm just
    # using a dictionary for simplicity in demonstrating the recipe part
    # extraction.
    recipe = defaultdict(lambda: None)

    page = lxml.html.parse(recipe_detail_page).getroot()
    url = page.get_element_by_id("ctl00_canonicalUrl").attrib['href']
    recipe['url'] = url

    title = page.get_element_by_id("itemTitle").text_content().strip()
    recipe['title'] = title

    author = page.get_element_by_id(
        "ctl00_CenterColumnPlaceHolder_recipe_lblSubmitter")
    author = author.text_content().strip()
    recipe['author'] = author

    description = page.get_element_by_id(
        "ctl00_CenterColumnPlaceHolder_recipe_divSubmitter")
    description = description.find_class('author-name')[0].getnext().text
    if description:
        description = description.strip()
        recipe['description'] = description

    servings = page.find_class("yield yieldform")
    if len(servings) == 1:
        recipe['servings'] = servings[0].text.strip()

    ingredients = page.find_class("ingredients")
    assert len(ingredients) == 1
    recipe['ingredients'] = []
    for i in ingredients[0].iter("li"):
        if i.text.strip():
            recipe['ingredients'].append(i.text.strip())

    steps = page.find_class("directions")
    assert len(steps) == 1
    steps = [s.text_content().strip() for s in steps[0].iter("li")]
    recipe['steps'] = steps
    recipe['num_steps'] = len(steps)

    recipe['ingredients_text'] = "\n".join(recipe['ingredients'])
    recipe['steps_text'] = "\n".join(steps)

    prep_time = page.find_class("prepTime")
    if len(prep_time) == 1:
        recipe['prep_time'] = time_to_minutes(prep_time[0].getnext().text)

    cook_time = page.find_class("cookTime")
    if len(cook_time) == 1:
        recipe['cook_time'] = time_to_minutes(cook_time[0].getnext().text)

    total_time = page.find_class("totalTime")
    if len(total_time) == 1:
        recipe['total_time'] = time_to_minutes(total_time[0].getnext().text)

    return recipe


def main():
    usage = "usage: %prog [options] files"
    parser = OptionParser(usage=usage)
    parser.add_option("--database", dest="database_url",
                      default='sqlite:///test_database.sqlite')
    parser.add_option("--logfile", dest="log_filename",
                      default='recipe_import.log')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    (options, args) = parser.parse_args()
    # Setup the database
    db = Database(options.database_url)
    # Configure logging
    logging.basicConfig(filename=options.log_filename, level=logging.INFO)
    if options.verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logging.getLogger().addHandler(console)
    if not args:
        sys.stderr.write("Please specify one or more pages downloaded from "
                         "AllRecipes.com\n")
        exit(-1)
    if len(args) > 1:
        filenames = args
    else:
        filenames = glob.iglob(args[0])
    for filename in filenames:
        if not os.path.isfile(filename):
            sys.stderr.write("%s must be a valid filename\n" % filename)
            exit(-1)
        recipe_file = open(filename)
        recipe_parts = extract_recipe_parts(recipe_file)
        try:
            db.add_from_recipe_parts(recipe_parts)
            logging.info("Imported recipe %s from %s" %
                (recipe_parts['title'], filename))
        except DuplicateRecipeException:
            logging.warn("Recipe in %s is a duplicate; skipping." % filename)
        recipe_file.close()


if __name__ == "__main__":
    main()
