"""
Creative Dialogue manager, is an alternate dialogue mgr which is eventually
intended to merge functionality with our main branch.  It is intended to
work on two extremes.  First to provide a quick and dirty functional system
that delivers some recipes, and provides minimal functionality a'la the 
old mamabot.  It should be there by the end of this week.

Second, it will start adding some intelligence features not provided by 
our current branch dialogue mgr.   These could include - a more intelligent
curiosity agent, that does a better job at finding out the wants and needs
of the client, provides agents with personalities, provides new creative 
recipes that are different than any of the existing recipes.
"""
import logging
import cPickle
from types import *
# probably wont use this for now.
# will instead try to create dialogue using the snlg.py.

# not sure if I will be using this yet.
from nlg import ContentPlanMessage

class QuestionSet(object):
    def __init__(self):
        """Creates a list of questions to discover some factoid

            by using SNLG.
        """
        pass

class Factoid(object):
    """Factoids are facts that we want to discover based on curiosity"""
    def __init__(self, the_type, categ=None):
        """
            NOT YET IMPLEMENTED.
            The factoids contain methods and a user factoid ontology.

            It will include data allowing the generation of questions that fill 
            the fields.  A type of constraint based ontology will cause the 
            inter-related fill to autofill according to some sort of 
            resolution - ideally this will involve some sort of fuzzy logic.

            The fields will involve the following types.
            Possible types are: 
                str: a string 
                lovehate: -1..1  # -1 is hate, 0 is neutral, 1 is love
                lst: a list of items, typically food_lovehate.
                food_lovehate: a food_item, lovehate pair.
            categ is the category of the kind of items to put in the list.
                This list is a list of factoids of this category.
            Somehow we are going to have a list of questions that will 
                lead to the necessary answers.
            For now, we will start with a very simple implementation 
            leading to non-impressive dialogue.
        """
        pass

class PatienceTrigger(object):
    """This class is utilized to evaluate whether the user is impatient

       If the user is impatient we will trigger the delivery of a recipe.
    """

    def __init__(self):
        pass

class UserModel(object):
    """
    Contains data describes tastes and likes of user.
    """

    # One of the forced greeting speeches is always the start.
    first_greeting = \
        "Welcome to the Creative Cooking Advisor.  Our goal is to based on\n" \
        + "your tastes and preferences provide you with advise on cooking recipes that\n" \
        + "will suit your wants and needs.  At any time you can say: 'creative on' or\n" \
        + "'creative off' to enable or disable my creative functions. \n" \
        + "Are you a new user?\n"

    # response = yes_or_no
    # if (neither_yes_or_no):
    #    NLG(tell_him_to_answer_yes_or_no, neutral)
    #    print("dog %s cat" % string).

    greetings = (
        'Insert a list of greetings here.\n'
    )

    def __init__(self):
        self.lasting_attrib = {
            'user_name':            Factoid(StringType, None),  
                # constraint: ('has FirstName or has LastName')
            'agent_personality_preference': Factoid(StringType, None),
                # formal, familiar (maybe a tad much), sadistic, insecure 
            'first_name':           Factoid(StringType, None),  
            'last_name':            Factoid(StringType, None),
            # 
            # below replace with the right type.
            'glucose_intolerance':  Factoid(StringType, None),
            'losing_weight':        Factoid(StringType, None),
            'gaining_weight':       Factoid(StringType, None),
            'diabetic':             Factoid(StringType, None),
            #
            'like_meat':            Factoid(StringType, None),
            'like_vegie':           Factoid(StringType, None),
            'like_shellfish':       Factoid(StringType, None),
            'like_spice':           Factoid(StringType, None),
            'is_vegetarian':        Factoid(StringType, None),
            #
            'meat_list':            Factoid(StringType, None),
            'fish_list':            Factoid(StringType, None),
            'shellfish_list':       Factoid(StringType, None),
            'spice_list':           Factoid(StringType, None),
            'cuisine_country_list': Factoid(StringType, None),
            #
            'lose_weight':          Factoid(StringType, None),
            'gain_weight':          Factoid(StringType, None),
            'patience':             Factoid(StringType, None),
            #
            'sadistic':             Factoid(StringType, None),
            'flirtatious':          Factoid(StringType, None),
            'nerdy':                Factoid(StringType, None),
            'valley_girl':          Factoid(StringType, None),
        }

        #######################################################################
        # This are the starting sets that will be changed dynamically to create
        # better dialogs. 
        # Accept questions about valid users.
        #
        greeting_factoids = {
            'user_name':                    100,    # Must be a valid file_name say up to 8
                                                    # characters, underscore, or digit
            'agent_personality_preference': 100,
            'first_name':                   100, 
            'last_name':                    100, 
        }

        dietary_restriction = {
            'glucose_intolerance':          100, 
            'losing_weight':                100,
            'gaining_weight':               100,
            'diabetic':                     100,
        }

        like_preferences = {
            'like_meat':        30,
            'like_vegie':       50,
            'like_shellfish':   50,
            'like_spice':       50,
            'is_vegetarian':    50, 
        }

        list_preferences = { 
            # importance, Value, constraint
            'meat_list':            30,
            'fish_list':            50,
            'shellfish_list':       50,
            'spice_list':           50,
            'cuisine_country_list': 70,
        }

        cuisine_preferences = {
            'countries':            50,
            'type':                 50,
        }

        other_preferences = {
            'patient':     30,
        }

        agent_preference = {
            'sadistic':                     100, 
            'flirtatious':                  100,
            'nerdy':                        100,
            'valley_girl':                  100,
        }

    def saving_user(self):
        """When quitting, or changing user, we save this user.
       
        This saves the preferences of a user, so that they can be
        restored later.
        Must make sure - that the users directory exists.
        """
        cPickle.dump( self, open( "users/" + self.user + ".p", "wb" ) )

    def restoring_user(self):
        """Once user is known, restore his data from the user list.

        Based on this data the new dialogue will begin\n
        You cannot call this until the user is known.
        The first thing to be done here will be to check if this user
        exists.
        """
        self =  cPickle.load(open( "users/" + self.user + ".p")) 

    def ingredient_suggestions(self):
        pass

    def __init__(self, db, logger):
        pass

    def curious(self):
        """curious tries to output user information statistically

           It uses a model based on what it doesn't know about the user, and 
           what it wants to know according to a variety of priorities.
           It results in a question, and a desire to ask questions.
        """
        pass

    def user_greeting(object):
        """
        Provides a greeting with the purpose, to learn who the user is, and 
        provide a desired assistant based on the personality of the user.
        """

        pass

class CreativeManager(object):
    """
    Object that performs an alternate methodology to dialog management.

    It's goal is to implement - initially a quick parrot mode (contingency plan), 
    and an alternate Multimodal Creative engine - more edgy than the current
    plan - that will provide creative recipes.

    """

    def __init__(self, db, logger, nlu=None, nlg=None, dm=None):
        """
        Create a new Creative Manager, it allows using standard nlu, nlg, and dm
        or bypassing them.  For now we are using the same one.

        >>> from database import Database
        >>> db = Database('sqlite:///:memory:')
        >>> bot = CreativeManager(db, logging.getLogger())
        >>> response = bot.handle_input("Hi!")

        """
        self.db = db
        self.log = logger
        self.nlu = nlu
        self.nlg = nlg
        self.dm = dm
        self.current_state = None
        self.user_name = None

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state
        self.log = logging.getLogger(self.log)

    def plan_response(self, parsed_input):
        """
        Given a list of parsed representations of user input, return a content
        plan representing the content to be expressed in response to the user.
        """
        # The actual DM implementation could look something like this:
        # submodules = [] # Every submodule (i.e. greeter, recipe searcher)
        #                 # implements some common interface.
        # cannidate_plans = []
        # for module in submodules:
        #     cannidate_plans.append(module.plan_response(parsed_input))
        # Decide between the cannidate plans
        # Return a plan

        # This is a simple finite state DM for demoing the chat interface.
        # This will be replaced as soon as a real DM is written.
        
        # Currently this does not take advantage of message types
        
        if self.current_state == 'wait_for_user_name':
            self.user_name = parsed_input[0].raw_input_string
            self.current_state = 'echo_user_input'
            content_plan = ContentPlanMessage("greet_user_by_name")
            content_plan.frame['user_name'] = self.user_name
            return content_plan
        else:
            if not self.user_name:
                self.current_state = 'wait_for_user_name'
                return ContentPlanMessage("ask_for_name")
            else:
                content_plan = ContentPlanMessage("echo_user_input")
                content_plan.frame['last_user_input'] = \
                    parsed_input[0].raw_input_string
                return content_plan

    def generate_response(self, content_plan):
        """
        Given a content plan representing the content to be expressed,
        return a generated utterance.
        """
        # TODO: implement sentence planner, surface realizer
        if content_plan.msg_type == "ask_for_name":
            return "What's your name?"
        elif content_plan.msg_type == "echo_user_input":
            template = 'You said:\n    "%s"'
            return template % content_plan.frame['last_user_input']
        elif content_plan.msg_type == "greet_user_by_name":
            template = "It's nice to meet you, %s."
            return template % content_plan.frame['user_name']
        else:
            return "I didn't understand what you just said."

    def respond(self, user_input):
        ##########################################################
        # for now we test this with the regular nlu, dm, and nlg
        # which have been passed. Later we will try experimental versions.
        ##########################################################
        self.log.debug('%12s = "%s"' % ('user_input', user_input))
        parsed_input = self.nlu.parse_input(user_input) 
        self.log.debug('%12s = "%s"' % ('parsed_input', parsed_input))
        content_plan = self.dm.plan_response(parsed_input) 
        self.log.debug('%12s = "%s"' % ('content_plan', content_plan))
        bot_response = self.nlg.generate_response(content_plan) 
        return('CR:' + bot_response)

