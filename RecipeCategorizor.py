#import freebase #used to access the freebase database
import nltk #durp
import re #used for regex splitting
import sqlite3 #import the sqlite3 libraries
from operator import itemgetter #used for list sorting

def getCuisine(recipe,DEBUG=0):
   """
   My attempt at pydoc.
   function getCuisine
   arguments: recipe
      An array that is a list of words (could be title, could be ingredients)
      such as:
      ["Apple Pie Spice","Prosciutto", "black pepper"]
   returns: an array of strings (0 or more) which is the list of cuisines
   that are associated with this recipe, as well as the frequency of
   occurrances. 
      ["Italian":1]
   """
   
   cats = [] #the map for the cuisines. This will hold frequencies of cuisines
   connection = sqlite3.connect("ingredients.db") #connect to the ingredientsdb
   c = connection.cursor() #do that connection thing

   if(DEBUG): print "getCuisine::Input Recipe: " + str(recipe)
   
   for word in recipe: #go through the input and start querying sqlite database

      #Check if there are any words like "American" or "Japanese" in there!
      #Note: How should we handle this?
      for w in checkAdjectivals([word]):
         cats.append(w);
      
      c = connection.cursor() #connect
      #make an sql query
      query = "SELECT cuisine FROM ingredients WHERE name='{0}'".format(word)
      if(DEBUG):print "getCuisine::query- " + query
      c.execute(query)
      #result = freebase.mqlread(query) #query the freebase db
      #clean up the array
      for w in c:
         if(DEBUG):print "getCuisine::Query Results: " + str(w)
         for cui in w:
            if(len(cui) > 0):
	       for word in cui.split(','):
                  if(DEBUG):print "getCuisine:: innermost for Adding: " + word
                  cats.append(word)
   #count the ingredients (solves issues like non-unique keys), counts up
   #all the occurrances. ie: {...'Italian':1,...,'Italian':1} becomes
   # {...,'Italian':2,....
   result = countIngredients(cats)
   return result

def countIngredients(ing):
   """
   function countIngredients(ing)
   helper function for 'getCuisine' function
   arguments: ing
      ing is an array of ingredients in key:value pairing. 'Cuisine':Count
   """
   dict={}
   for word in ing:
      addToDict(dict,word)
   return dict

def checkAdjectivals(words):
    """
    function checkAdjectivals(words)
    checks if any of the words are in the list of country adjectivals. These
    are located in "ListOfAdj" and this should be located in the same dir,
    or modify the line:
    adjList = loadFileToArray("ListOfAdj")

    arguments: Array of words to check against
    returns: dictionary of results with counts.
    """
    adjList = loadFileToArray("ListOfAdj")
    results = {}
    for word in words:
	if(word in adjList):
	    addToDict(results, word)
    return results
	
	

def loadFileToArray(file):
    """
    function loadFileToArray(file)
    reads a file into an array. Makes it super easy to do things.
    arguments: file
    returns: an array consisting of each line of the file
    """
    f = open(file, 'r')
    result = []
    for line in f:
	result.append(re.sub('\n','',line))
    return result


def readLines(filename,limit=5):
   """
   function readLines
   used for reading all the lines in a file that is the list of recipies
   in their raw file name. Which is in the format of 
   '1-2-3-Cheddar-Broccoli-Casserole.html'
   """
   result={}
   wordsCount={}
   totLimit=limit
   counter=1;
   f = open(filename,'r')
   for line in f:
      line = cleanLine(line)
      for word in line.split():
         addToDict(wordsCount,word)
         #print "{0}/{1} Operating on line: {2}".format(counter,totLimit,line)
         #print "Cuisine: " + str(getCuisine(line))
         result = dict_add([result,getCuisine(line)])
         limit -= 1
         if(limit < 0): break
         counter+=1
         print "Ingredients Result:"
         printDictionary(result)
         print "Words Result: "
         printDictionary(wordsCount)

#add word to dictionary
def addToDict(dict,word):
   """
   function addToDict
   adds (string)argument 2 to (dict)argument 1. Does checking if it's
   already in there, it'll just increment the count
   """
   if(dict.has_key(word)):
      dict[word] = dict[word] + 1
   else:
      dict[word] = 1


#dict add from Josh. Merges two dicts
def dict_add(dicts):
   """
   >>> dict1 = {'key1' : 1}
   >>> dict2 = {'key1' : 3}
   >>> dict3 = {'key2' : 4}
   >>> dict_add([dict1, dict2, dict3])
   {'key2': 4, 'key1': 4}
   """
   keys = set()
   for d in dicts:
      for k in d.keys():
         keys.add(k)
   merged = {}
   for k in keys:
      merged[k] = 0
   for d in dicts:
      for (key, value) in d.items():
         merged[key] += value
   return merged


def cleanLine(line):
   """
   function cleanLine
   split up the line, which comes in like this:
    '10-Minute-Zesty-Salsa.html' so we need to nuke the special chars
   returns the cleaned up line
   ***now depreciated, but keep it in here just in case***
   """
   res = re.split('[\n]|[-]|[\.html]{5}',line)
   while "" in res:
      res.remove("")
      result = ""
   for r in res:
      result += r + " "
   return result

def printDictionary(dict):
   sList = sorted(dict.items(), key=itemgetter(1))
   for lines in sList:
      print "[{0},{1}]".format(lines[0],lines[1])
   
# Example usage!:
printDictionary(getCuisine(["Apple", "Prosciutto", "Pasta", "Stuffed Chicken Breast", "Israeli", "American"]))
