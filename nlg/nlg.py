import os
import random
from simplenlg import NPPhraseSpec, PPPhraseSpec, SPhraseSpec, Realiser, gateway, InterrogativeType

class NLG(object):

    def __init__(self):
        """
        Creates a new Natural Lanaguage Generator.
        
        conf_responses: a list of preconfigured templates to express 
                        acknowledgement of input or action
        aff_responses: a list of preconfigured templates to express 
                       affirmation or to say 'yes'
        neg_responses: a list of preconfigured templates to express
                       decline of request or action or to say 'no'
        """

        self.conf_responses = ['You got it',
                              'As you wish',
                              'You don\'t have to ask me twice',
                              'Of course',
                              'Okay',
                              'Acknowledged']
 
        self.aff_responses = ['Yes',
                              'Yeah',
                              'Very much so',
                              'Affirmative']

        self.neg_responses = ['No',
                              'Nah',
                              'Negative',
                              'I\'m afraid not']

        self.words = {'name':'Jeraziah',
                      'subject':'you', 
                      'verb':'prefer', 
                      'object':'recipes',
                      'preposition':'that contains',
                      'objmodifiers':['Thai'],
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

        phrase.setInterrogative(InterrogativeType.YES_NO)
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

        output = []

        ptime_str = "Prep Time: %i minutes" % (recipe.prep_time)
        ctime_str = "Cook Time: %i minutes" % (recipe.cook_time)
        ttime_str = "Total Time: %i minutes" % (recipe.total_time)
        cuisines_str = 'Cuisines: ' + ', '.join(c.name for c in recipe.cuisines)

        output.append('Here is the recipe you requested: \n')
        output.append(recipe.title + ' by ' + recipe.author)
        output.append(cuisines_str + '\n')
        output.append(recipe.description + '\n')
        output.append(recipe.ingredients_text + '\n')
        output.append(recipe.servings)
        output.append(ptime_str)
        output.append(ctime_str)
        output.append(ttime_str)

        return '\n'.join(output)

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

        >>> nlg = NLG()
        >>> words = {'subject':'you', 
        ...         'verb':'prefer', 
        ...         'object':'recipes',
        ...         'preposition':'that contains',
        ...         'objmodifiers':['Thai']
        ...         'prepmodifiers':['potatoes','celery','carrots'],
        ...         'adverbs':['confidently'],
        >>> nlg.generate('yes_no', words)
        'Do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        >>> nlg.generate('how', words)
        'How do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        """

        if utter_type.lower() == 'greet':
            if 'name' in keywords:
                return'Hello, %s!' % (keywords['name'])
            else:
                return 'Hello there!'
            return

        if utter_type.lower() == 'echo':
            if 'lastinput' in keywords:
                return keywords['lastinput']

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
            utterance.setInterrogative(InterrogativeType.YES_NO)
        elif utter_type.lower() == 'how':
            utterance.setInterrogative(InterrogativeType.HOW)
        elif utter_type.lower() == 'what':
            utterance.setInterrogative(InterrogativeType.WHAT)
        elif utter_type.lower() == 'where':
            utterance.setInterrogative(InterrogativeType.WHERE)
        elif utter_type.lower() == 'who':
            utterance.setInterrogative(InterrogativeType.WHO)
        elif utter_type.lower() == 'why':
            utterance.setInterrogative(InterrogativeType.WHY)
        elif utter_type.lower() == 'confirm':
            return self.acknowledge(keywords)
        elif utter_type.lower() == 'affirm':
            return self.affirm(keywords)
        elif utter_type.lower() == 'decline':
            return self.decline(keywords)

        target.addModifier(preposition)
        utterance.setSubject(keywords['subject'])
        utterance.setVerb(keywords['verb'])
        if 'adverbs' in keywords:
            for modifier in keywords['adverbs']:
                utterance.addModifier(modifier)
        utterance.addComplement(target)
        
        realiser = Realiser()
        output = realiser.realiseDocument(utterance).strip()
        return output

    def acknowledge(self, keywords):
        """
        Returns an utterance of acknowledgement at random.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        acknowledgement = random.choice(self.conf_responses)
        if 'name' in keywords:
            acknowledgement += random.choice([', ' + keywords['name'], ''])
        return acknowledgement + random.choice(['.', '!'])

    def affirm(self, keywords):
        """
        Returns an utterance of affirmation at random.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        affirmation = random.choice(self.aff_responses)
        if 'name' in keywords:
            affirmation += random.choice([', ' + keywords['name'], ''])
        return affirmation + random.choice(['.', '!'])

    def decline(self, keywords):
        """
        Returns an utterance of denial or decline of action.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        decline = random.choice(self.neg_responses)
        if 'name' in keywords:
            decline += random.choice([', ' + keywords['name'], ''])
        return decline + random.choice(['.', '!'])

class NLGException(Exception):
    """
    Base class for throwing exceptions related to the NLG
    """

    pass
