import random
import types
import logging
import nlg 
from nlg import NaturalLanguageGenerator
from nlg import ContentPlanMessage as CPM
# from nlu.messages import SearchMessage, YesNoMessage, SystemMessage
# nlu = NaturalLanguageUnderstander(confidenceThreshold, logger)
# nlu = NaturalLanguageUnderstander(0.5, logger)
# dm = DialogueManager(db, logger.getChild('dm'))

logger = logging.getLogger()
nlg = NaturalLanguageGenerator(logger)

# from nlu.messages import SearchMessage, YesNoMessage, SystemMessage
#  def generate_response(self, content_plan_or_plans):
#  def handle_content_plan_message(self, content_plan):
#  def generate_recipe(self, recipe):
#  def generate(self, utter_type, keywords):
#  def acknowledge(self):
#  def affirm(self):
#  def decline(self):
#  def goodbye(self):
#  def unknown(self):
#  def clarify(self, keywords):
#  def summarize_query(self, query):
#  def specify_recipe(self, keywords):
#  def search_fail(self, keywords):
#  def search_related(self, keywords):
#  def advise(self):
#  def change_tone(self, tone):
#  def tone_str(self, key):
#  def clean_str(self, string):
#
#  self.tone = 'normal'
#  self.msg_type = msg_type
#
# Pre configured words:
#######################
#  self.search_verbs = ['look for', ...	 - Search verbs
#  self.conf_responses = ['You got it',  - Confirmation words.
#  self.aff_responses = ['Yes',		 - Affirmation words.
#  self.neg_responses = ['No',		 - Negation words.
# 
#  self.words = {
#	'name': 'Jeraziah',
#       'subject': 'you',
#       'verb': 'prefer',
#       'object': 'recipes',
#       'preposition': 'that contains',
#       'objmodifiers': ['Thai'],
#       'prepmodifiers': ['potatoes', 'celery', 'carrots'],
#	'adverbs': ['confidently'],
#	'lastinput': 'Sing me a song.',
#       'clarify_cat': 'meat',
#	'clarify_list': ['chicken', 'beef', 'pork']}
#
#   self.query = {'include_ingredients': ['chicken', 'pineapple', 'pepper'],
#
#
# def clean_str(self, string):
#
# 'yes_no', 'how', 'what', 'where', 'who', 'why'

def out_quest(utter_type='yes_no',
     subject='',         # user ?
     adverbs = [],       # ['confidently'],
     verb='',
     # Object build
     object = '',        # recipe
     preposition = '',   # e.g that contains
     objmodifier = '',   # e.g Thay 
     prepmodifiers = [], # ['potatoes', 'celery', 'carrots'],
):
    keywords = {'subject':subject, 'adverbs':adverbs, 'verb':verb, 
            'object':object, 'preposition':preposition, 
            'objmodifier':objmodifier, 'prepmodifiers':prepmodifiers}
    nlg.generate(utter_type, keywords) 

def nlg_user_name(pre='', cap=False):
    """returns a name for the user in the mood of the agent

    if cap is True then set the first letter to be capitalized. 
    """
    # if the mood is not set - it returns emtpy. 
    name = nlg.tone_str('adjectives') 
    if cap:
       name = name.capitalize() 
    return name + ' ' + nlg.tone_str('names')

def out(msg):
    """Simple echoed message"""
    return CPM('echo', message=msg)

def out_yes():
    """respond in the affirmative."""
    return CPM('affirm')

def out_no():
    """respond in the negative."""
    return CPM('decline')
   
def out_ack():
    return CPM('acknowledge')

def out_bye():
    return (CPM('goodbye'))

def out_smy_qry(query_dict):
    """
    Takes a dict of queries to be summarized according to DB item types.
    
    See Database.get_recipes() for the possible keys and values
    that can be used. e.g.: {'include_ingredients': ['egg']}
    """
    assert type(query_dict) is types.DictType, "out_smy_qry item_list is not a dict type"
    # Might want to check the value is a list.
    return CPM('summarize_query', query=query_dict)

def out_specify(recipe_list=[]):
    return CPM('specify_recipe', query={'include_ingredients': recipe_list})

def out_unknown(recipe_list=[]):
    """Returns a message indicating the last item is unknown."""
    return nlg.unknown()

def out_clarify(categ='ingredient', item_list=[]):
    """Clarify which of several choices the user will want.
    Right now, the category may only be ingredients.
    Later we may want to add dish category, type of cooking category 
    and more.   Clarify_list takes a list of ingredients to choose from.
    For instance you want to clarify whether you want to choose between
    chicken, beef and pork.
    e.g. clarify_list=['chicken', 'beef', 'pork']
    """
    assert type(item_list) is types.ListType, "clarify item_list is not a list"
    return CPM('clarify', clarify_cat=categ, clarify_list=item_list)

def out_recipe(recipes):
    """Output 1 or more recipes"""
    # *EYE: process this to find out - what I passed, if it is a list of #'s
    # then convert them to recipe objects.
    if type(recipes) is types.ListType:
        return CPM('specify_recipe', recipes=recipes)
    else: # return a single recipe
        return CPM('specify_recipe', recipes=[recipes])

#################################################################################
#                      THESE ARE NOT IMPLEMENTED YET.
#################################################################################
def out_related_search(related_item_list):
    """NOT IMPLEMENTED YET"""
    return CPM('related_search', related_items=related_item_list)

def out_related_search(related_items):
    """NOT IMPLEMENTED YET"""
    return CPM('search_fail')

def out_advise():
    """NOT IMPLEMENTED YET: provides some culinary advise as we leave program"""
    return CPM('advise')
#################################################################################

def fun_test(mode, recipe):
    global agent_mode
    agent_mode = mode
    query_dict = {'include_ingredients': ['egg', 'carrots']}
    preference_list=['chicken', 'beef', 'pork']
    a_quest = \
        out_quest(
            subject=("The " + nlg_user_name()), 
            adverbs = ['absolutely'],
            verb='is', 
            # Object build
            object = 'sure',    # recipe
            preposition = '',   # e.g that contains
            objmodifier = '',   # e.g Thai 
            prepmodifiers = [], # ['potatoes', 'celery', 'carrots'],
        ),
    if a_quest is None:
       print("a_quest is None")
    else:
       print(a_quest)

    out_list = [
        out("So, " + nlg_user_name() + ", ask me about recipes and ingredients!"),
        out(nlg_user_name(cap=True) + ", ask me about recipes and ingredients!"),
        out_yes(),
        out_no(),
        out_ack(),
        out_bye(),
        # This requires some experience.
        # See Database.get_recipes() for the possible keys and values
        # here is an example. 
        out_smy_qry(query_dict),
        # out_clarify:  ask for preference amongst a group, like e.g. for meats:
        out_clarify(preference_list),
        # need to pass a recipe object or a list of them.
        out_recipe(recipe),
        # related search is not implemented.
        # related_items = ['chicken', 'beef', 'pork']
        # out_related_search(related_items),
        # out_advise is not implemented.
        # out_advise(),
        #
        # out_unknown(),
    ]
    return(out_list)

def testit():
    mode='cruel'
    print("\n\n%s\n###########################\n" % mode)
    nlg.change_tone(mode) # cruel, affectionate, normal
    for o in fun_test(mode, mock_recipe): print(nlg.generate_response(o))
    mode='affectionate'
    print("\n\n%s\n###########################\n" % mode)
    nlg.change_tone(mode) # cruel, affectionate, normal
    for o in fun_test(mode, mock_recipe): print(nlg.generate_response(o))
    mode='normal'
    print("\n\n%s\n###########################\n" % mode)
    nlg.change_tone(mode) # cruel, affectionate, normal
    for o in fun_test(mode, mock_recipe): print(nlg.generate_response(o))

if __name__ == "__main__":
    ###########################################
    ###########################################
    # create a dummy recipe
    class Mock(object): pass
    mock_recipe = Mock()
    mock_recipe.title = "Chocolate Chip Cookies"
    mock_recipe.author = "Grandma"

    testit()

