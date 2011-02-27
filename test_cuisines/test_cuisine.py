#!/opt/ActivePython-2.6/bin/python2.6
# make sure you first have build the database
# test_database.sqlite with: allrecipes.py
import re
from database import Database
from nlu import *
db = Database("sqlite:///../test_database.sqlite")
# recipes = db.get_recipes(total_time=(30, 60))
cuis=db.get_cuisines()
all_cuis=cuis.all()
cu2rec={}
for cu in all_cuis:
    # cu2rec[cu.name] = cu2rec.get(cu.title, []) 
    # cu2rec[cu.name].append(cu.recipes)
    print(cu.name)
    cu2rec[cu.name] = cu.recipes

for cu_name, recipes in cu2rec.items():
     print(cu.name)
     for recipe in recipes:
         print("\t%s" % recipe.title)

