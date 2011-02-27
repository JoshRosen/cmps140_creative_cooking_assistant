import atexit
import os
from subprocess import Popen, PIPE
from py4j.java_gateway import JavaGateway, GatewayClient, java_import
from simplenlg import NPPhraseSpec, PPPhraseSpec, SPhraseSpec, Realiser, gateway

class NLG(object):

    def __init__(self):

        """
        Create a new Natural Lanaguage Generator
        """

        self.words = {'name':'Jeraziah',
                      'subject':'you', 
                      'verb':'prefer', 
                      'object':'recipes',
                      'preposition':'that contains',
                      'objmodifiers':['Thai']
                      'prepmodifiers':['potatoes','celery','carrots'],
                      'adverbs':['confidently'],
                      'lastinput':'Sing me a song.'}
        print 'nlg creation successful'

    def test(self):

        """
        A test of the SimpleNLG server.
        Constructs the following sentence:
        Do you want Mexican breakfast recipes that contain cheese, salsa,
        and eggs?
        """

        phrase = SPhraseSpec()

        recipe_type = NPPhraseSpec("recipes")
        recipe_type.addModifier("Mexican")
        recipe_type.addModifier("breakfast")

        prep = PPPhraseSpec()
        prep.setPreposition("that contain")
        prep.addComplement("cheese")
        prep.addComplement("salsa")
        prep.addComplement("eggs")
        recipe_type.addModifier(prep)

        phrase.setInterrogative(gateway.jvm.InterrogativeType.YES_NO)
        phrase.setSubject("you")
        phrase.setVerb("want")
        phrase.addComplement(recipe_type)

        realiser = Realiser()
        output = realiser.realiseDocument(phrase).strip()
        print output

    def generate_recipe(self, recipe):

        """
        Receives a Recipe object and displays its contents to the user.
        """

        print 'Here is the recipe you requested:'
        print recipe.title
        print recipe.author
        print recipe.description
        print recipe.ingredients
        print recipe.cuisines
        print recipe.ingredients_text
        print recipe.servings
        print recipe.prep_time
        print recipe.cook_time
        print recipe.total_time

    def generate(self, utter_type, keywords):

        """
        Input: a type of inquiry to create and a dictionary of keywords.
        Types of inquiries include 'what', 'who', 'where', 'why', 'how', 
        and 'yes/no' questions. Alternatively, 'none' can be specified to
        generate a declarative statement.
        The dictionary is essentially divided into three core parts: the
        subject, the verb, and the object. Modifiers can be specified to these
        parts (adverbs, adjectives, etc). Additionally, an optional
        prepositional phrase can be specified.

        Example: 
        words = {'subject':'you', 
                 'verb':'prefer', 
                 'object':'recipes',
                 'preposition':'that contains',
                 'objmodifiers':['Thai']
                 'prepmodifiers':['potatoes','celery','carrots'],
                 'adverbs':['confidently'],
        
        generate('yes_no', words) will produce:
        "Do you prefer Thai recipes that contains potatoes, celery,
         and carrots?"

        generate('how', words) will produce:
        "How do you prefer Thai recipes that contains potatoes, celery,
         and carrots?"
        """

        if utter_type.lower() == 'greet':
            if 'name' in keywords:
                print 'Hello, %s!' % (keywords['name'])
            else:
                print 'Hello there!'
            return

        if utter_type.lower() == 'echo':
            if 'lastinput' in keywords:
                print keywords['lastinput']
            return

        utterance = SPhraseSpec()
        subject = NPPhraseSpec(keywords['subject'])
        target = NPPhraseSpec(keywords['object'])
        preposition = PPPhraseSpec()
        
        if 'preposition' in keywords:
            preposition.setPreposition(keywords['preposition'])

        if 'prepmodifiers' in keywords:
            for modifier in keywords['prepmodifiers']:
                preposition.addComplement(modifier)

        if 'submodifiers' in keywords:
            for modifier in keywords['submodifiers']:
                subject.addModifier(modifier)

        if 'objmodifiers' in keywords:
            for modifier in keywords['objmodifiers']:
                target.addModifier(modifier)

        if utter_type.lower() == 'yes_no':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.YES_NO)
        elif utter_type.lower() == 'how':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.HOW)
        elif utter_type.lower() == 'what':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.WHAT)
        elif utter_type.lower() == 'where':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.WHERE)
        elif utter_type.lower() == 'who':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.WHO)
        elif utter_type.lower() == 'why':
            utterance.setInterrogative(gateway.jvm.InterrogativeType.WHY)

        target.addModifier(preposition)
        utterance.setSubject(subject)
        utterance.setVerb(keywords['verb'])
        if 'adverbs' in keywords:
            for modifier in keywords['adverbs']:
                utterance.addModifier(modifier)
        utterance.addComplement(target)
        
        realiser = Realiser()
        output = realiser.realiseDocument(utterance).strip()
        print output

class NLGException(Exception):
    """
    Base class for throwing exceptions related to the NLG
    """
    pass
