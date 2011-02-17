import freebase #used to access the freebase database
import nltk #durp
import re #used for regex splitting
from operator import itemgetter #used for list sorting


#query = {
#    "name" : "prosciutto",
#    "type" : "/food/ingredient",
#    "cuisine" : []
#    }
#result = freebase.mqlread(query)
#print result["cuisine"]

def getCuisine(recipe):
    """
    My attempt at pydoc.
    function getCuisine
    arguments: recipe
    A string that is a list of words (could be title, could be ingredients)
    returns: an array of strings (0 or more) which is the list of cuisines that are associated with this recipe, as well as the frequency of occurrances. 
    """
    tokens = nltk.word_tokenize(recipe)
    #tagged = nltk.pos_tag(tokens)
    cats = [] #the map for the cuisines. This will hold frequencies of cuisines
    for w in tokens:
      query = [{
         "name" : w,
         "type" : "/food/ingredient",
         "cuisine" : []
      }]
      result = freebase.mqlread(query)
      #clean up the array
      for w in result:
	  if(len(w["cuisine"]) > 0):
	      for c in w["cuisine"]:
		  cats.append(c)
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
	print "{0}/{1} Operating on line: {2}".format(counter,totLimit,line)
	print "Cuisine: " + str(getCuisine(line))
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
    
	

      
#getCuisine("Apple and Prosciutto Stuffed Chicken Breast")
#readLines("RecipesList",100000)
#print(getCuisine(""))
